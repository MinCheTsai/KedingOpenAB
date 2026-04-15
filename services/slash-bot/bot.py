"""🐌 比奇堡查詢服務 — Slash Command Bot"""
import logging
import os
import traceback

import discord
from discord import app_commands

from query_usage import (
    ACTIVITY_CATEGORIES,
    get_activity_data,
    get_tier_limit,
    get_usage_data,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
ALLOWED_CHANNEL_ID = os.environ.get("SLASH_BOT_CHANNEL_ID")

RANK_MEDALS = {0: "🥇", 1: "🥈", 2: "🥉"}


class SlashBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            # 先同步指令到 guild
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            # 再清除全域指令殘留
            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            logging.info(f"✅ 指令已同步至 guild {GUILD_ID}（全域已清除）")
        else:
            await self.tree.sync()
            logging.info("✅ 指令已全域同步")

    async def on_ready(self):
        logging.info(f"🐌 查詢服務上線！({self.user})")


bot = SlashBot()


def wrong_channel(interaction: discord.Interaction) -> bool:
    if ALLOWED_CHANNEL_ID and str(interaction.channel_id) != ALLOWED_CHANNEL_ID:
        return True
    return False


def make_progress_bar(pct: float, length: int = 10) -> str:
    filled = int(round(pct / 100 * length))
    filled = max(0, min(length, filled))
    return f"`{'█' * filled + '░' * (length - filled)}` {pct:.0f}%"


# ─── /help ───────────────────────────────────────────────

@bot.tree.command(name="help", description="列出所有可用指令")
async def help_cmd(interaction: discord.Interaction):
    if wrong_channel(interaction):
        await interaction.response.send_message("🐌 喵～請到指定頻道使用指令喔", ephemeral=True)
        return
    embed = discord.Embed(title="🐌 可用指令", color=0x00B894)
    embed.add_field(
        name="/usage [acp] [range]",
        value=(
            "額度消耗報表\n"
            "`acp`：kiro（預設）\n"
            "`range`：`1`=本月, `2`=近2月, `week:1`=近1週"
        ),
        inline=False,
    )
    embed.add_field(
        name="/activity [acp] [range]",
        value=(
            "功能使用分析\n"
            "`acp`：kiro（預設）\n"
            "`range`：`1`=本月(預設), `2`=近2月, `week:1`=近1週"
        ),
        inline=False,
    )
    embed.set_footer(text="喵～有問題請找海綿寶寶")
    await interaction.response.send_message(embed=embed)


# ─── /usage ──────────────────────────────────────────────

@bot.tree.command(name="usage", description="查詢 Kiro 使用額度")
@app_commands.describe(
    acp="ACP 名稱（預設 kiro）",
    range="時間範圍：1=本月, 2=近2月, week:1=近1週",
)
async def usage_cmd(interaction: discord.Interaction, acp: str = "kiro", range: str = None):
    if wrong_channel(interaction):
        await interaction.response.send_message("🐌 喵～請到指定頻道使用指令喔", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        if acp.lower() != "kiro":
            await interaction.followup.send(f"🐌 `{acp}` 尚未支援喵～目前只支援 kiro")
            return

        logging.info(f"/usage acp={acp} range={range}")
        data = get_usage_data(range)
        embeds = _build_usage_embeds(data)
        await interaction.followup.send(embeds=embeds[:10])
        logging.info("/usage 回覆完成")
    except Exception as e:
        logging.error(f"/usage 失敗：{e}\n{traceback.format_exc()}")
        try:
            await interaction.followup.send(f"❌ 查詢失敗：{e}")
        except Exception:
            logging.error("followup 也失敗了")


def _build_usage_embeds(data: dict) -> list[discord.Embed]:
    embeds = []
    for period in data["periods"]:
        lines = []
        users = period["users"]
        for i, u in enumerate(users):
            limit = get_tier_limit(u["tier"])
            pct = u["credits"] / limit * 100 if limit else 0
            medal = RANK_MEDALS.get(i, "　")
            bar = make_progress_bar(pct)
            lines.append(
                f"{medal} **{u['user']}**（{u['tier']}）\n"
                f"　　💰 {u['credits']:.1f} / {limit}　{bar}\n"
                f"　　💬 訊息 {u['messages']}　🗂️ 對話 {u['conversations']}"
            )
        embed = discord.Embed(
            title=f"🐌 Kiro 額度報表 — {period['label']}",
            description="\n\n".join(lines) if lines else "沒有資料喵～",
            color=0x00B894,
        )
        embed.set_footer(text="額度每月 1 日重置 | 喵～")
        embeds.append(embed)
    return embeds


# ─── /activity ───────────────────────────────────────────

@bot.tree.command(name="activity", description="分析 Kiro 的使用方式")
@app_commands.describe(
    acp="ACP 名稱（預設 kiro）",
    range="時間範圍：1=本月(預設), 2=近2月, week:1=近1週",
)
async def activity_cmd(interaction: discord.Interaction, acp: str = "kiro", range: str = None):
    if wrong_channel(interaction):
        await interaction.response.send_message("🐌 喵～請到指定頻道使用指令喔", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        if acp.lower() != "kiro":
            await interaction.followup.send(f"🐌 `{acp}` 尚未支援喵～目前只支援 kiro")
            return

        logging.info(f"/activity acp={acp} range={range}")
        data = get_activity_data(range)
        embeds = _build_activity_embeds(data)
        if embeds:
            await interaction.followup.send(embeds=embeds[:10])
        else:
            await interaction.followup.send("🐌 沒有找到任何活動資料喵～")
        logging.info("/activity 回覆完成")
    except Exception as e:
        logging.error(f"/activity 失敗：{e}\n{traceback.format_exc()}")
        try:
            await interaction.followup.send(f"❌ 查詢失敗：{e}")
        except Exception:
            logging.error("followup 也失敗了")


def _build_activity_embeds(data: dict) -> list[discord.Embed]:
    embeds = []
    for period in data["periods"]:
        lines = []
        for u in period["users"]:
            user_lines = [f"**{u['user']}**"]
            has_data = False
            for cat_name, cols in ACTIVITY_CATEGORIES.items():
                # 只顯示非零的類別
                nonzero = {c: u.get(c, 0) for c in cols if u.get(c, 0) > 0}
                if nonzero:
                    has_data = True
                    parts = "　".join(f"`{_col_label(k)}`:{v}" for k, v in nonzero.items())
                    user_lines.append(f"　　📌 {cat_name}：{parts}")
            if has_data:
                lines.append("\n".join(user_lines))
            else:
                lines.append(f"**{u['user']}**\n　　（無活動紀錄）")

        embed = discord.Embed(
            title=f"📊 Kiro 功能使用分析 — {period['label']}",
            description="\n\n".join(lines) if lines else "沒有資料喵～",
            color=0x6C5CE7,
        )
        embed.set_footer(text="喵～")
        embeds.append(embed)
    return embeds


def _col_label(col: str) -> str:
    """把欄位名轉成簡短標籤"""
    labels = {
        "chat_aicodelines": "AI程式碼行",
        "chat_messagesinteracted": "互動訊息",
        "chat_messagessent": "發送訊息",
        "inline_aicodelines": "AI程式碼行",
        "inline_acceptancecount": "採納數",
        "inline_suggestionscount": "建議數",
        "inlinechat_acceptanceeventcount": "採納次數",
        "inlinechat_acceptedlineadditions": "採納新增行",
        "inlinechat_acceptedlinedeletions": "採納刪除行",
        "inlinechat_totaleventcount": "總次數",
        "dev_acceptanceeventcount": "採納次數",
        "dev_acceptedlines": "採納行數",
        "dev_generatedlines": "生成行數",
        "dev_generationeventcount": "生成次數",
        "codefix_acceptanceeventcount": "採納次數",
        "codefix_acceptedlines": "採納行數",
        "codefix_generatedlines": "生成行數",
        "codereview_findingscount": "發現數",
        "codereview_succeededeventcount": "成功次數",
        "codereview_failedeventcount": "失敗次數",
        "testgeneration_acceptedtests": "採納測試",
        "testgeneration_generatedtests": "生成測試",
        "testgeneration_eventcount": "次數",
        "docgeneration_eventcount": "次數",
        "docgeneration_acceptedlineadditions": "採納行數",
        "transformation_eventcount": "次數",
        "transformation_linesgenerated": "生成行數",
        "transformation_linesingested": "輸入行數",
    }
    return labels.get(col, col.split("_", 1)[-1])


if __name__ == "__main__":
    bot.run(TOKEN)
