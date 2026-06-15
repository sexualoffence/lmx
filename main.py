import discord
import discord_ios
from discord.ext import commands
import asyncio
import os

from config import TOKEN, get_prefix

intents = discord.Intents.all()

bot = commands.AutoShardedBot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None
)

async def load_extensions():
    for folder in ("cogs", "events"):
        if not os.path.exists(folder):
            continue

        for file in os.listdir(folder):
            if file.endswith(".py"):
                extension = f"{folder}.{file[:-3]}"

                try:
                    await bot.load_extension(extension)
                    print(f"Loaded {extension}")
                except Exception as e:
                    print(f"Failed to load {extension}: {e}")

@bot.event
async def on_ready():
    synced = await bot.tree.sync()

    print(f"Logged in as {bot.user}")
    print(f"Guilds: {len(bot.guilds)}")
    print(f"Shards: {bot.shard_count}")
    print(f"Synced {len(synced)} slash commands")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())