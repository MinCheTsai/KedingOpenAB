"""🐚 神奇海螺 (Magic Conch) — 容器健康監控 & 生命管理 Bot"""
import asyncio
import json
import logging
import os
import traceback
from datetime import datetime, timedelta, timezone

import discord
import docker
from discord import app_commands
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

# 限定使用的頻道（急診室）
ALLOWED_CHANNEL_ID = os.environ.get("CONCH_CHANNEL_ID")

# OpenAI for summarization
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# 限定使用的頻道（急診室）
ALLOWED_CHANNEL_ID = os.environ.get("CONCH_CHANNEL_ID")

# 允許執行危險操作的使用者 ID（米哥）
ADMIN_USER_IDS = [int(uid.strip()) for uid in os.environ.get("CONCH_ADMIN_IDS", "").split(",") if uid.strip()]
# 允許執行 heal 的 role ID
OPERATOR_ROLE_IDS = [int(rid.strip()) for rid in os.environ.get("CONCH_OPERATOR_ROLE_IDS", "").split(",") if rid.strip()]

# 角色暱稱 → 容器名稱對應
ROLE_MAP = {
    "海綿寶寶": "bob",
    "bob": "bob",
    "派大星": "patrick",
    "patrick": "patrick",
    "章魚哥": "squidward",
    "squidward": "squidward",
    "珊迪": "sandy",
    "sandy": "sandy",
    "泡芙老師": "puff",
    "puff": "puff",
    "小蝸": "slash-bot",
    "gary": "slash-bot",
    "企微": "wecom-bot",
    "wecom": "wecom-bot",
    "gateway": "gateway",
}

# 管理的容器清單（agent 角色，不含企微 bot / gateway）
MANAGED_CONTAINERS = ["bob", "patrick", "squidward", "sandy", "puff", "slash-bot"]


def get_docker_client() -> docker.DockerClient:
    docker_host = os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock")
    return docker.DockerClient(base_url=docker_host)


def resolve_container_name(name: str) -> str | None:
    return ROLE_MAP.get(name.lower().strip())


def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.id in ADMIN_USER_IDS


def is_operator(interaction: discord.Interaction) -> bool:
    if is_admin(interaction):
        return True
    if hasattr(interaction.user, "roles"):
        user_role_ids = [r.id for r in interaction.user.roles]
        return any(rid in user_role_ids for rid in OPERATOR_ROLE_IDS)
    return False


def wrong_channel(interaction: discord.Interaction) -> bool:
    if ALLOWED_CHANNEL_ID and str(interaction.channel_id) != ALLOWED_CHANNEL_ID:
        return True
    return False


class MagicConch(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            logging.info(f"✅ 指令已同步至 guild {GUILD_ID}")
        else:
            await self.tree.sync()
            logging.info("✅ 指令已全域同步")

    async def on_ready(self):
        logging.info(f"🐚 神奇海螺已甦醒！({self.user})")


bot = MagicConch()


def _display_name(container_name: str) -> str:
    names = {
        "bob": "海綿寶寶",
        "patrick": "派大星",
        "squidward": "章魚哥",
        "sandy": "珊迪",
        "puff": "泡芙老師",
        "slash-bot": "小蝸",
        "wecom-bot": "企微Bot",
        "gateway": "Gateway",
    }
    return names.get(container_name, container_name)


def _status_emoji(status: str) -> str:
    return {
        "running": "🟢",
        "exited": "🔴",
        "restarting": "🟡",
        "paused": "⏸️",
        "dead": "💀",
    }.get(status, "❓")


def _check_health(container) -> str | None:
    """檢查容器 log 是否有已知錯誤 pattern，回傳異常描述或 None。"""
    if container.status != "running":
        return None

    error_patterns = [
        "Internal error", "internal error", "-32603",
        "LoginFailure", "Improper token",
        "FATAL", "panic",
    ]

    try:
        since = datetime.now(timezone.utc) - timedelta(minutes=5)
        logs = container.logs(since=since, timestamps=False).decode("utf-8", errors="replace")
        if not logs.strip():
            logs = container.logs(tail=50, timestamps=False).decode("utf-8", errors="replace")
        for pattern in error_patterns:
            if pattern in logs:
                return pattern
    except Exception:
        pass
    return None


def _get_container_stats(container) -> dict:
    """取得容器的 CPU / Memory 使用量（非 streaming）。"""
    try:
        stats = container.stats(stream=False)
        # Memory
        mem_usage = stats["memory_stats"].get("usage", 0)
        mem_limit = stats["memory_stats"].get("limit", 1)
        mem_mb = mem_usage / (1024 * 1024)
        mem_pct = (mem_usage / mem_limit) * 100 if mem_limit else 0
        # CPU
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"].get("system_cpu_usage", 0) - stats["precpu_stats"].get("system_cpu_usage", 0)
        num_cpus = stats["cpu_stats"].get("online_cpus", 1)
        cpu_pct = (cpu_delta / system_delta) * num_cpus * 100 if system_delta > 0 else 0
        return {"mem_mb": mem_mb, "mem_pct": mem_pct, "cpu_pct": cpu_pct}
    except Exception:
        return {"mem_mb": 0, "mem_pct": 0, "cpu_pct": 0}


def _format_uptime(started_at: str) -> str:
    """將 StartedAt 轉為人類可讀的 uptime。"""
    try:
        started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - started
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except Exception:
        return "?"


def _get_status_line(name: str, client: docker.DockerClient, verbose: bool = True) -> str:
    """產生單一容器的狀態行。verbose=True 時包含資源資訊。"""
    try:
        c = client.containers.get(name)
        emoji = _status_emoji(c.status)
        started_at = c.attrs["State"].get("StartedAt", "")
        restart_count = c.attrs.get("RestartCount", 0)
        health_issue = _check_health(c)

        # 基本資訊
        uptime = _format_uptime(started_at)
        base = f"{emoji} **{_display_name(name)}**"

        if c.status != "running":
            return f"{base} — {c.status}"

        if health_issue:
            base = f"⚠️ **{_display_name(name)}** — 偵測到 `{health_issue}`"

        if verbose:
            stats = _get_container_stats(c)
            detail = f"uptime {uptime} | CPU {stats['cpu_pct']:.1f}% | RAM {stats['mem_mb']:.0f}MB ({stats['mem_pct']:.1f}%)"
            if restart_count > 0:
                detail += f" | restarts: {restart_count}"
            return f"{base} — {detail}"
        else:
            return f"{base} — running (uptime {uptime})"
    except docker.errors.NotFound:
        return f"❓ **{_display_name(name)}** — 不存在"


# ─── /conch-status ───────────────────────────────────────

@bot.tree.command(name="conch-status", description="🐚 查看容器狀態")
@app_commands.describe(target="角色名稱，不填則查看全部")
async def status_cmd(interaction: discord.Interaction, target: str = ""):
    if wrong_channel(interaction):
        await interaction.response.send_message("🐚 ...請到急診室。", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        client = get_docker_client()
        targets = MANAGED_CONTAINERS if not target else None

        if targets:
            lines = [_get_status_line(name, client) for name in targets]
            client.close()
            await interaction.followup.send(f"🐚 全員...回報。\n\n" + "\n".join(lines))
        else:
            container_name = resolve_container_name(target)
            if not container_name:
                client.close()
                await interaction.followup.send(f"🐚 ...不認識「{target}」。")
                return
            line = _get_status_line(container_name, client)
            client.close()
            await interaction.followup.send(f"🐚 {line}")
    except Exception as e:
        logging.error(f"/conch-status 失敗：{e}\n{traceback.format_exc()}")
        await interaction.followup.send(f"🐚 ...出了點問題。`{e}`")


# ─── /conch-logs ─────────────────────────────────────────

@bot.tree.command(name="conch-logs", description="🐚 查看容器近期 log")
@app_commands.describe(target="角色名稱，不填則查看全部（每個 5 行）", lines="行數（預設 20，上限 50）")
async def logs_cmd(interaction: discord.Interaction, target: str = "", lines: int = 20):
    if wrong_channel(interaction):
        await interaction.response.send_message("🐚 ...請到急診室。", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        client = get_docker_client()
        lines = min(lines, 50)

        if not target:
            # 全部：每個角色最後 5 行
            parts = []
            for name in MANAGED_CONTAINERS:
                try:
                    c = client.containers.get(name)
                    log_output = c.logs(tail=5, timestamps=False).decode("utf-8", errors="replace")
                    if len(log_output) > 300:
                        log_output = log_output[-300:]
                    parts.append(f"**{_display_name(name)}**\n```\n{log_output.strip() or '(無 log)'}\n```")
                except docker.errors.NotFound:
                    parts.append(f"**{_display_name(name)}** — 不存在")
            client.close()
            # Discord 訊息上限 2000 字，分批發送
            msg = "🐚 全員 log...\n\n" + "\n".join(parts)
            if len(msg) > 1900:
                # 分兩段
                mid = len(parts) // 2
                await interaction.followup.send("🐚 全員 log...\n\n" + "\n".join(parts[:mid]))
                await interaction.followup.send("\n".join(parts[mid:]))
            else:
                await interaction.followup.send(msg)
        else:
            container_name = resolve_container_name(target)
            if not container_name:
                client.close()
                await interaction.followup.send(f"🐚 ...不認識「{target}」。")
                return
            try:
                c = client.containers.get(container_name)
                log_output = c.logs(tail=lines, timestamps=False).decode("utf-8", errors="replace")
                if len(log_output) > 1900:
                    log_output = log_output[-1900:]
                client.close()
                await interaction.followup.send(
                    f"🐚 **{_display_name(container_name)}** 最近 {lines} 行 log：\n```\n{log_output}\n```"
                )
            except docker.errors.NotFound:
                client.close()
                await interaction.followup.send(f"🐚 ...{target}不存在。")
    except Exception as e:
        logging.error(f"/conch-logs 失敗：{e}\n{traceback.format_exc()}")
        await interaction.followup.send(f"🐚 ...讀取失敗。`{e}`")


# ─── /conch-heal ─────────────────────────────────────────

@bot.tree.command(name="conch-heal", description="🐚 重啟容器")
@app_commands.describe(target="角色名稱，不填則全員重啟（需確認）", confirm="全員重啟時輸入 yes 確認")
async def heal_cmd(interaction: discord.Interaction, target: str = "", confirm: str = ""):
    if wrong_channel(interaction):
        await interaction.response.send_message("🐚 ...請到急診室。", ephemeral=True)
        return
    if not is_operator(interaction):
        await interaction.response.send_message("🐚 ...不允許。", ephemeral=True)
        return

    if not target:
        # 全員重啟，需要管理員 + 確認
        if not is_admin(interaction):
            await interaction.response.send_message("🐚 ...全員重啟僅限管理員。", ephemeral=True)
            return
        if confirm.lower() != "yes":
            await interaction.response.send_message(
                "🐚 ...全員重啟需要確認。請加上 `confirm: yes`。", ephemeral=True
            )
            return
        await interaction.response.defer()
        try:
            client = get_docker_client()
            results = []
            for name in MANAGED_CONTAINERS:
                try:
                    c = client.containers.get(name)
                    c.restart(timeout=10)
                    results.append(f"✅ {_display_name(name)}")
                except docker.errors.NotFound:
                    results.append(f"❓ {_display_name(name)}（不存在）")
                except Exception as e:
                    results.append(f"❌ {_display_name(name)}（{e}）")
            client.close()
            await interaction.followup.send(f"🐚 ...全員重啟完畢。\n\n" + "\n".join(results))
        except Exception as e:
            logging.error(f"/conch-heal all 失敗：{e}\n{traceback.format_exc()}")
            await interaction.followup.send(f"🐚 ...失敗了。`{e}`")
    else:
        # 單一角色重啟
        await interaction.response.defer()
        try:
            container_name = resolve_container_name(target)
            if not container_name:
                await interaction.followup.send(f"🐚 ...不認識「{target}」。")
                return
            client = get_docker_client()
            container = client.containers.get(container_name)
            container.restart(timeout=10)
            client.close()
            await interaction.followup.send(f"🐚 ...{_display_name(container_name)}已重啟。")
        except docker.errors.NotFound:
            await interaction.followup.send(f"🐚 ...{target}不存在。")
        except Exception as e:
            logging.error(f"/conch-heal 失敗：{e}\n{traceback.format_exc()}")
            await interaction.followup.send(f"🐚 ...治療失敗。`{e}`")


# ─── /conch-archive ──────────────────────────────────────

ARCHIVE_MAX_MESSAGES = 300  # 最多讀取的訊息數用於摘要
SUMMARY_MODEL = "gpt-4o-mini"


async def _fetch_thread_messages(thread: discord.Thread, limit: int = ARCHIVE_MAX_MESSAGES) -> list[discord.Message]:
    """取得 thread 的訊息（從舊到新）。"""
    messages = []
    async for msg in thread.history(limit=limit, oldest_first=True):
        messages.append(msg)
    return messages


async def _summarize_messages(messages: list[discord.Message]) -> str:
    """用 OpenAI 產生對話摘要。"""
    if not openai_client:
        # Fallback: 取最後 20 則訊息的純文字
        recent = messages[-20:]
        lines = [f"{m.author.display_name}: {m.content[:100]}" for m in recent if m.content]
        return "（無法產生 AI 摘要，以下為最近對話）\n" + "\n".join(lines)

    # 準備對話內容（限制 token，取最近 100 則）
    recent = messages[-100:]
    conversation = "\n".join(
        f"[{m.created_at.strftime('%m/%d %H:%M')}] {m.author.display_name}: {m.content[:200]}"
        for m in recent if m.content
    )

    try:
        response = await openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一個對話摘要助手。請用繁體中文總結以下 Discord 對話，包含：\n"
                        "1. 討論主題\n"
                        "2. 目前進度/結論\n"
                        "3. 待辦事項或未解決的問題\n"
                        "4. 參與者各自的立場/貢獻\n"
                        "保持簡潔，不超過 500 字。"
                    ),
                },
                {"role": "user", "content": conversation},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        return response.choices[0].message.content or "（摘要產生失敗）"
    except Exception as e:
        logging.error(f"OpenAI 摘要失敗：{e}")
        # Fallback
        recent = messages[-10:]
        lines = [f"{m.author.display_name}: {m.content[:80]}" for m in recent if m.content]
        return f"（AI 摘要失敗：{e}）\n最近對話：\n" + "\n".join(lines)


def _get_bot_participants(messages: list[discord.Message]) -> set[int]:
    """找出 thread 中所有 bot 參與者的 user ID。"""
    bot_ids = set()
    for msg in messages:
        if msg.author.bot and msg.author.id != bot.user.id:  # 排除海螺自己
            bot_ids.add(msg.author.id)
    return bot_ids


@bot.tree.command(name="conch-archive", description="🐚 封存當前 thread，開新 thread 延續對話")
@app_commands.describe(reason="封存原因（選填）")
async def archive_cmd(interaction: discord.Interaction, reason: str = "對話過長"):
    # 這個指令不限急診室，任何 thread 都能用
    # 但必須在 thread 裡使用
    channel = interaction.channel
    if not isinstance(channel, discord.Thread):
        await interaction.response.send_message(
            "🐚 ...這個指令只能在 thread 裡使用。", ephemeral=True
        )
        return

    # 只有 operator 以上可以封存
    if not is_operator(interaction):
        await interaction.response.send_message("🐚 ...不允許。", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        thread = channel
        parent_channel = thread.parent

        # Step 1: 取得訊息
        messages = await _fetch_thread_messages(thread)
        msg_count = len(messages)

        if msg_count < 5:
            await interaction.followup.send("🐚 ...訊息太少，不需要封存。")
            return

        # Step 2: 產生摘要
        summary = await _summarize_messages(messages)

        # Step 3: 找出所有 bot 參與者
        bot_ids = _get_bot_participants(messages)
        mentions_str = " ".join(f"<@{uid}>" for uid in bot_ids)

        # Step 4: 在舊 thread 發結尾訊息
        new_thread_title = f"{thread.name}（續）" if len(thread.name) < 90 else thread.name[:87] + "…（續）"

        await thread.send(
            f"📦 **此對話已封存**（{reason}，共 {msg_count} 則訊息）\n"
            f"由 {interaction.user.mention} 執行封存。\n"
            f"討論將延續至新 thread。"
        )

        # Step 5: 在同頻道開新 thread（發一則訊息然後建 thread）
        # 組合新 thread 的開場訊息
        opener_content = (
            f"🔄 **延續討論**（封存自：{thread.name}）\n\n"
            f"{mentions_str}\n\n"
            f"**前情提要：**\n{summary}"
        )

        # Discord 訊息上限 2000 字
        if len(opener_content) > 1900:
            opener_content = opener_content[:1900] + "\n\n（摘要已截斷）"

        # 在 parent channel 發訊息並建立 thread
        new_msg = await parent_channel.send(opener_content)
        new_thread = await new_msg.create_thread(name=new_thread_title)

        # Step 6: 在新 thread 補充說明
        await new_thread.send(
            f"🐚 此 thread 延續自封存的對話。\n"
            f"原 thread：https://discord.com/channels/{interaction.guild_id}/{thread.id}\n"
            f"封存原因：{reason}\n"
            f"原訊息數：{msg_count}"
        )

        # Step 7: 回報完成
        await interaction.followup.send(
            f"🐚 ...封存完畢。\n"
            f"📦 原 thread：{msg_count} 則訊息已封存\n"
            f"🆕 新 thread：{new_thread.mention}\n"
            f"👥 已 mention {len(bot_ids)} 個 bot 參與者"
        )

        logging.info(
            f"/conch-archive: {interaction.user} 封存 thread {thread.id} "
            f"({msg_count} msgs) → 新 thread {new_thread.id}"
        )

    except Exception as e:
        logging.error(f"/conch-archive 失敗：{e}\n{traceback.format_exc()}")
        await interaction.followup.send(f"🐚 ...封存失敗。`{e}`")


if __name__ == "__main__":
    bot.run(TOKEN)
