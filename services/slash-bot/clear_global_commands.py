"""清除指定 bot 的全域 slash command 殘留

用法：
  docker exec slash-bot python clear_global_commands.py <BOT_TOKEN>

例如清除海綿寶寶的：
  docker exec slash-bot python clear_global_commands.py "$DISCORD_BOT_TOKEN_BOB"
"""
import sys

import discord


async def main(token: str):
    client = discord.Client(intents=discord.Intents.default())
    tree = discord.app_commands.CommandTree(client)

    @client.event
    async def on_ready():
        # 清除全域指令
        tree.clear_commands(guild=None)
        await tree.sync()
        print(f"✅ 已清除 {client.user} 的全域指令")
        await client.close()

    await client.start(token)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python clear_global_commands.py <BOT_TOKEN>")
        sys.exit(1)
    import asyncio
    asyncio.run(main(sys.argv[1]))
