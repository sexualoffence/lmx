import discord
from discord.ext import commands
from config import load_prefixes, DEFAULT_PREFIX

class PingEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.guild:
            return

        if message.content.strip() not in (
            f"<@{self.bot.user.id}>",
            f"<@!{self.bot.user.id}>"
        ):
            return

        prefixes = load_prefixes()
        current = prefixes.get(
            str(message.guild.id),
            DEFAULT_PREFIX
        )

        embed = discord.Embed(
            description=(
                f"<:dawnsmug:1506240625610330243> {message.author.mention} Dawn's prefix for this server is `{current}`\n"
                f"Use `/prefix set <prefix>` or `{current}prefix set <prefix>`"
            ),
            color=discord.Color(0xBAF0F7)
        )

        await message.reply(
            embed=embed,
            mention_author=False
        )

async def setup(bot):
    await bot.add_cog(PingEvent(bot))