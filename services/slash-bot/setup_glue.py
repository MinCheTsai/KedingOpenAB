"""🐌 Glue Table 管理腳本（冪等：DROP + CREATE）

用法：docker exec slash-bot python setup_glue.py
修改 schema 後重跑即可，不影響 S3 資料。
"""
import time

import boto3

REGION = "us-east-1"
WORKGROUP = "kiro-usage"
DATABASE = "kiro_usage"
BUCKET = "keding-kiro-user-activity-report-us-east-1"
ACCOUNT = "057336397271"
BASE = f"s3://{BUCKET}/user-reports/AWSLogs/{ACCOUNT}/KiroLogs"

athena = boto3.client("athena", region_name=REGION)

# ─── Table 定義 ──────────────────────────────────────────

TABLES = {
    "user_report": {
        "drop": f"DROP TABLE IF EXISTS {DATABASE}.user_report",
        "create": f"""
CREATE EXTERNAL TABLE {DATABASE}.user_report (
  `date` string,
  `userid` string,
  `client_type` string,
  `chat_conversations` string,
  `credits_used` string,
  `overage_cap` string,
  `overage_credits_used` string,
  `overage_enabled` string,
  `profileid` string,
  `subscription_tier` string,
  `total_messages` string
)
PARTITIONED BY (`year` string, `month` string, `day` string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('quoteChar'='"', 'separatorChar'=',')
STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION '{BASE}/user_report/us-east-1/'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.year.type' = 'integer',
  'projection.year.range' = '2025,2030',
  'projection.month.type' = 'integer',
  'projection.month.range' = '1,12',
  'projection.month.digits' = '2',
  'projection.day.type' = 'integer',
  'projection.day.range' = '1,31',
  'projection.day.digits' = '2',
  'storage.location.template' = '{BASE}/user_report/us-east-1/${{year}}/${{month}}/${{day}}/00',
  'skip.header.line.count' = '1'
)
""",
    },
    "by_user_analytic": {
        "drop": f"DROP TABLE IF EXISTS {DATABASE}.by_user_analytic",
        "create": f"""
CREATE EXTERNAL TABLE {DATABASE}.by_user_analytic (
  `userid` string,
  `date` string,
  `chat_aicodelines` string,
  `chat_messagesinteracted` string,
  `chat_messagessent` string,
  `codefix_acceptanceeventcount` string,
  `codefix_acceptedlines` string,
  `codefix_generatedlines` string,
  `codefix_generationeventcount` string,
  `codereview_failedeventcount` string,
  `codereview_findingscount` string,
  `codereview_succeededeventcount` string,
  `dev_acceptanceeventcount` string,
  `dev_acceptedlines` string,
  `dev_generatedlines` string,
  `dev_generationeventcount` string,
  `docgeneration_acceptedfileupdates` string,
  `docgeneration_acceptedfilescreations` string,
  `docgeneration_acceptedlineadditions` string,
  `docgeneration_acceptedlineupdates` string,
  `docgeneration_eventcount` string,
  `docgeneration_rejectedfilecreations` string,
  `docgeneration_rejectedfileupdates` string,
  `docgeneration_rejectedlineadditions` string,
  `docgeneration_rejectedlineupdates` string,
  `inlinechat_acceptanceeventcount` string,
  `inlinechat_acceptedlineadditions` string,
  `inlinechat_acceptedlinedeletions` string,
  `inlinechat_dismissaleventcount` string,
  `inlinechat_dismissedlineadditions` string,
  `inlinechat_dismissedlinedeletions` string,
  `inlinechat_rejectedlineadditions` string,
  `inlinechat_rejectedlinedeletions` string,
  `inlinechat_rejectioneventcount` string,
  `inlinechat_totaleventcount` string,
  `inline_aicodelines` string,
  `inline_acceptancecount` string,
  `inline_suggestionscount` string,
  `testgeneration_acceptedlines` string,
  `testgeneration_acceptedtests` string,
  `testgeneration_eventcount` string,
  `testgeneration_generatedlines` string,
  `testgeneration_generatedtests` string,
  `transformation_eventcount` string,
  `transformation_linesgenerated` string,
  `transformation_linesingested` string
)
PARTITIONED BY (`year` string, `month` string, `day` string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('quoteChar'='"', 'separatorChar'=',')
STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION '{BASE}/by_user_analytic/us-east-1/'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.year.type' = 'integer',
  'projection.year.range' = '2025,2030',
  'projection.month.type' = 'integer',
  'projection.month.range' = '1,12',
  'projection.month.digits' = '2',
  'projection.day.type' = 'integer',
  'projection.day.range' = '1,31',
  'projection.day.digits' = '2',
  'storage.location.template' = '{BASE}/by_user_analytic/us-east-1/${{year}}/${{month}}/${{day}}/00',
  'skip.header.line.count' = '1'
)
""",
    },
}


# ─── 執行邏輯 ────────────────────────────────────────────

def run_ddl(sql: str, label: str = ""):
    """執行 DDL 並等待完成"""
    resp = athena.start_query_execution(QueryString=sql.strip(), WorkGroup=WORKGROUP)
    qid = resp["QueryExecutionId"]
    while True:
        status = athena.get_query_execution(QueryExecutionId=qid)
        state = status["QueryExecution"]["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if state != "SUCCEEDED":
        reason = status["QueryExecution"]["Status"].get("StateChangeReason", "")
        raise RuntimeError(f"{label} 失敗: {state} - {reason}")
    return state


def main():
    print(f"🐌 Glue Table 管理 — database: {DATABASE}\n")
    for name, ddl in TABLES.items():
        print(f"  ⏳ {name}: DROP...", end=" ", flush=True)
        run_ddl(ddl["drop"], f"{name} DROP")
        print("CREATE...", end=" ", flush=True)
        run_ddl(ddl["create"], f"{name} CREATE")
        print("✅")
    print(f"\n🎉 完成！共 {len(TABLES)} 個 table")


if __name__ == "__main__":
    main()
