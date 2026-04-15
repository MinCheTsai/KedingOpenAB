"""清除指定 bot 在指定 guild 的 slash command

用法：
  python clear_guild_commands.py <BOT_TOKEN> <GUILD_ID>
"""
import asyncio
import sys

import discord


async def main(token: str, guild_id: str):
    client = discord.Client(intents=discord.Intents.default())
    tree = discord.app_commands.CommandTree(client)

    @client.event
    async def on_ready():
        guild = discord.Object(id=int(guild_id))
        tree.clear_commands(guild=guild)
        await tree.sync(guild=guild)
        print(f"✅ 已清除 {client.user} 在 guild {guild_id} 的指令")
        await client.close()

    await client.start(token)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python clear_guild_commands.py <BOT_TOKEN> <GUILD_ID>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
