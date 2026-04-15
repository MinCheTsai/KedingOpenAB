"""🐌 Kiro 資料查詢層 — Athena 查詢 + S3 快取"""
import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import boto3

REGION = "us-east-1"
DATABASE = "kiro_usage"
WORKGROUP = "kiro-usage"
CACHE_BUCKET = "keding-kiro-user-activity-report-us-east-1"
CACHE_PREFIX = "kiro-usage-cache/"

USER_MAP = {
    "0704fae8-c031-701c-38a9-fe8c6c0e32c5": "MinChe Tsai",
    "37943aa8-9011-7067-cdcc-d548211de86a": "sherry li",
    "97f42a28-00c1-70db-d2fe-fbc99d9278c1": "Hsuan Wu",
    "f7040a28-80d1-7029-e9a2-ce35b6c55b5b": "wahow chen",
}

TIER_LIMITS = {
    "PRO": 1000,
    "PRO_PLUS": 2000,
    "PRO+": 2000,
    "POWER": 10000,
}

s3 = boto3.client("s3", region_name=REGION)
athena = boto3.client("athena", region_name=REGION)


# ─── 通用工具 ────────────────────────────────────────────

def _run_athena(sql: str) -> list[list[str]]:
    """執行 Athena SQL，回傳 raw rows（不含 header）"""
    resp = athena.start_query_execution(QueryString=sql, WorkGroup=WORKGROUP)
    qid = resp["QueryExecutionId"]
    while True:
        status = athena.get_query_execution(QueryExecutionId=qid)
        state = status["QueryExecution"]["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if state != "SUCCEEDED":
        reason = status["QueryExecution"]["Status"].get("StateChangeReason", "")
        raise RuntimeError(f"Athena 查詢失敗: {state} - {reason}")

    rows = []
    paginator = athena.get_paginator("get_query_results")
    first_page = True
    for page in paginator.paginate(QueryExecutionId=qid):
        page_rows = page["ResultSet"]["Rows"]
        if first_page:
            page_rows = page_rows[1:]
            first_page = False
        for row in page_rows:
            rows.append([col.get("VarCharValue", "") for col in row["Data"]])
    return rows


def _cache_key(prefix: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"{CACHE_PREFIX}{prefix}_{today}.json"


def _read_cache(prefix: str):
    try:
        resp = s3.get_object(Bucket=CACHE_BUCKET, Key=_cache_key(prefix))
        return json.loads(resp["Body"].read())
    except s3.exceptions.NoSuchKey:
        return None


def _write_cache(prefix: str, data):
    s3.put_object(
        Bucket=CACHE_BUCKET,
        Key=_cache_key(prefix),
        Body=json.dumps(data, ensure_ascii=False, indent=2),
        ContentType="application/json",
    )


def get_tier_limit(tier: str) -> int:
    t = tier.upper().replace(" ", "_") if tier else ""
    return TIER_LIMITS.get(t, TIER_LIMITS.get("PRO", 1000))


# ─── Range 解析 ──────────────────────────────────────────

def parse_range(range_str: str | None) -> dict:
    """
    解析 range 參數，回傳 {type, start, end, group_by, periods}
    - None / "1"        → 本月 1 日 ~ 昨天
    - "2"               → 2 個月前 1 日 ~ 昨天，按月 group
    - "week:1"          → 過去 1 週
    - "week:2"          → 過去 2 週，按週 group
    - "month:2"         → 2 個月前 1 日 ~ 昨天，按月 group（同 "2"）
    """
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    if not range_str or range_str == "1":
        # 本月
        start = today.replace(day=1)
        return {
            "type": "month",
            "start": start,
            "end": yesterday,
            "group_by": None,
            "periods": [(f"{start.strftime('%m/%d')}~{yesterday.strftime('%m/%d')}", start, yesterday)],
        }

    if range_str.startswith("week:"):
        n = int(range_str.split(":")[1])
        start = today - timedelta(weeks=n)
        if n == 1:
            return {
                "type": "week",
                "start": start,
                "end": yesterday,
                "group_by": None,
                "periods": [(f"{start.strftime('%m/%d')}~{yesterday.strftime('%m/%d')}", start, yesterday)],
            }
        # 多週：按週 group（週一~週日）
        periods = []
        cursor = start
        # 對齊到週一
        cursor = cursor - timedelta(days=cursor.weekday())
        while cursor <= yesterday:
            week_end = min(cursor + timedelta(days=6), yesterday)
            label = f"{cursor.strftime('%m/%d')}({_weekday_zh(cursor)})~{week_end.strftime('%m/%d')}({_weekday_zh(week_end)})"
            periods.append((label, cursor, week_end))
            cursor = cursor + timedelta(days=7)
        return {
            "type": "week",
            "start": start,
            "end": yesterday,
            "group_by": "week",
            "periods": periods,
        }

    # "month:N" 或純數字 "N"
    raw = range_str.replace("month:", "")
    n = int(raw)
    # N 個月前的 1 日
    y, m = today.year, today.month
    for _ in range(n - 1):
        m -= 1
        if m <= 0:
            m += 12
            y -= 1
    start = datetime(y, m, 1).date()

    if n == 1:
        return {
            "type": "month",
            "start": start,
            "end": yesterday,
            "group_by": None,
            "periods": [(f"{start.strftime('%m/%d')}~{yesterday.strftime('%m/%d')}", start, yesterday)],
        }

    # 多月：按月 group
    periods = []
    cursor_y, cursor_m = start.year, start.month
    while True:
        m_start = datetime(cursor_y, cursor_m, 1).date()
        if cursor_m == 12:
            m_end = datetime(cursor_y + 1, 1, 1).date() - timedelta(days=1)
        else:
            m_end = datetime(cursor_y, cursor_m + 1, 1).date() - timedelta(days=1)
        m_end = min(m_end, yesterday)
        if m_start > yesterday:
            break
        label = f"{m_start.strftime('%m/%d')}~{m_end.strftime('%m/%d')}"
        periods.append((label, m_start, m_end))
        cursor_m += 1
        if cursor_m > 12:
            cursor_m = 1
            cursor_y += 1
    return {
        "type": "month",
        "start": start,
        "end": yesterday,
        "group_by": "month",
        "periods": periods,
    }


def _weekday_zh(d) -> str:
    return ["一", "二", "三", "四", "五", "六", "日"][d.weekday()]


# ─── /usage 查詢（user_report）────────────────────────────

def _date_filter_sql(start, end) -> str:
    """產生 partition 篩選 SQL"""
    return (
        f"year BETWEEN '{start.year}' AND '{end.year}' "
        f"AND CAST(year || month || day AS integer) "
        f"BETWEEN {start.strftime('%Y%m%d')} AND {end.strftime('%Y%m%d')}"
    )


def query_usage(start, end) -> list[dict]:
    """查詢 user_report 指定日期範圍"""
    sql = f"""
    SELECT date, userid, client_type, subscription_tier,
           CAST(credits_used AS double) AS credits_used,
           CAST(total_messages AS bigint) AS total_messages,
           CAST(chat_conversations AS bigint) AS chat_conversations
    FROM {DATABASE}.user_report
    WHERE {_date_filter_sql(start, end)}
    ORDER BY date DESC, userid
    """
    rows = _run_athena(sql)
    return [
        {
            "date": r[0],
            "user": USER_MAP.get(r[1], r[1]),
            "client_type": r[2],
            "tier": r[3],
            "credits_used": round(float(r[4]), 2) if r[4] else 0,
            "total_messages": int(r[5]) if r[5] else 0,
            "chat_conversations": int(r[6]) if r[6] else 0,
        }
        for r in rows
    ]


def get_usage_data(range_str: str | None = None) -> dict:
    """回傳 {range_info, periods: [{label, users: [{user, tier, credits, messages, conversations}]}]}"""
    r = parse_range(range_str)
    cache_label = f"usage_{r['start']}_{r['end']}"
    cached = _read_cache(cache_label)
    if cached:
        return cached

    result = {"range_info": {"start": str(r["start"]), "end": str(r["end"])}, "periods": []}

    for label, p_start, p_end in r["periods"]:
        data = query_usage(p_start, p_end)
        agg = _aggregate_usage(data)
        ranked = sorted(agg.values(), key=lambda x: x["credits"], reverse=True)
        result["periods"].append({"label": label, "users": ranked})

    _write_cache(cache_label, result)
    return result


def _aggregate_usage(data: list[dict]) -> dict:
    by_user = defaultdict(lambda: {"user": "", "credits": 0.0, "messages": 0, "conversations": 0, "tier": ""})
    for r in data:
        u = by_user[r["user"]]
        u["user"] = r["user"]
        u["credits"] += r["credits_used"]
        u["messages"] += r["total_messages"]
        u["conversations"] += r["chat_conversations"]
        if r["tier"]:
            u["tier"] = r["tier"]
    return dict(by_user)


# ─── /activity 查詢（by_user_analytic）────────────────────

ACTIVITY_CATEGORIES = {
    "Chat": ["chat_aicodelines", "chat_messagesinteracted", "chat_messagessent"],
    "Inline 補全": ["inline_aicodelines", "inline_acceptancecount", "inline_suggestionscount"],
    "InlineChat": [
        "inlinechat_acceptanceeventcount", "inlinechat_acceptedlineadditions",
        "inlinechat_acceptedlinedeletions", "inlinechat_totaleventcount",
    ],
    "Dev（Agent）": ["dev_acceptanceeventcount", "dev_acceptedlines", "dev_generatedlines", "dev_generationeventcount"],
    "CodeFix": ["codefix_acceptanceeventcount", "codefix_acceptedlines", "codefix_generatedlines"],
    "CodeReview": ["codereview_findingscount", "codereview_succeededeventcount", "codereview_failedeventcount"],
    "TestGeneration": [
        "testgeneration_acceptedtests", "testgeneration_generatedtests",
        "testgeneration_eventcount",
    ],
    "DocGeneration": ["docgeneration_eventcount", "docgeneration_acceptedlineadditions"],
    "Transformation": ["transformation_eventcount", "transformation_linesgenerated", "transformation_linesingested"],
}

# 所有 activity 欄位（展平）
ALL_ACTIVITY_COLS = []
for cols in ACTIVITY_CATEGORIES.values():
    ALL_ACTIVITY_COLS.extend(cols)
ALL_ACTIVITY_COLS = list(dict.fromkeys(ALL_ACTIVITY_COLS))  # 去重保序


def query_activity(start, end) -> list[dict]:
    """查詢 by_user_analytic 指定日期範圍，回傳每人彙總"""
    col_sums = ", ".join(f"SUM(CAST({c} AS bigint)) AS {c}" for c in ALL_ACTIVITY_COLS)
    sql = f"""
    SELECT userid, {col_sums}
    FROM {DATABASE}.by_user_analytic
    WHERE {_date_filter_sql(start, end)}
    GROUP BY userid
    ORDER BY userid
    """
    raw = _run_athena(sql)
    results = []
    for r in raw:
        uid = r[0]
        row = {"user": USER_MAP.get(uid, uid)}
        for i, col in enumerate(ALL_ACTIVITY_COLS):
            row[col] = int(r[i + 1]) if r[i + 1] else 0
        results.append(row)
    return results


def get_activity_data(range_str: str | None = None) -> dict:
    """回傳 {range_info, periods: [{label, users: [dict]}]}"""
    r = parse_range(range_str)
    cache_label = f"activity_{r['start']}_{r['end']}"
    cached = _read_cache(cache_label)
    if cached:
        return cached

    result = {"range_info": {"start": str(r["start"]), "end": str(r["end"])}, "periods": []}

    for label, p_start, p_end in r["periods"]:
        users = query_activity(p_start, p_end)
        result["periods"].append({"label": label, "users": users})

    _write_cache(cache_label, result)
    return result
