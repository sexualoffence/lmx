import discord
import json
from discord.ext import commands
from views.confirm import ConfirmView
from datetime import timedelta
from datetime import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):

        async def do_lock(interaction: discord.Interaction):
            overwrite = interaction.channel.overwrites_for(
                interaction.guild.default_role
            )

            overwrite.send_messages = False

            await interaction.channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite
            )

            embed = discord.Embed(
                description=f"<:check:1514888247401123923> {interaction.channel.mention} has been locked.",
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description="Are you sure you want to lock this channel?",
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_lock)
        )

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):

        async def do_unlock(interaction: discord.Interaction):
            overwrite = interaction.channel.overwrites_for(
                interaction.guild.default_role
            )

            overwrite.send_messages = None

            await interaction.channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite
            )

            embed = discord.Embed(
                description=f"<:check:1514888247401123923> {interaction.channel.mention} has been unlocked.",
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description="Are you sure you want to unlock this channel?",
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_unlock)
        )

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

    @commands.command(
        name="purge",
        aliases=["clear"]
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):

        if amount < 1:
            return await ctx.send(
                embed=discord.Embed(
                    description="Amount must be greater than 0.",
                    color=discord.Color.red()
                )
            )

        async def do_purge(interaction: discord.Interaction):

            deleted = await interaction.channel.purge(limit=amount + 1)

            embed = discord.Embed(
                description=f"<:check:1514888247401123923> Deleted {len(deleted) - 1} messages.",
                color=0xA3EB7B
            )

            await interaction.channel.send(
                embed=embed,
                delete_after=5
            )

            try:
                await interaction.message.delete()
            except:
                pass

        embed = discord.Embed(
            description=f"Are you sure you want to delete **{amount}** messages?",
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_purge)
        )

    @purge.error
    async def purge_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.purge <amount>`",
                    color=discord.Color.red()
                )
            )

    @commands.command(name="hide")
    @commands.has_permissions(manage_channels=True)
    async def hide(self, ctx):

        async def do_hide(interaction: discord.Interaction):

            overwrite = interaction.channel.overwrites_for(
                interaction.guild.default_role
            )

            overwrite.view_channel = False

            await interaction.channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite
            )

            embed = discord.Embed(
                description=f"<:check:1514888247401123923> {interaction.channel.mention} has been hidden.",
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description="Are you sure you want to hide this channel?",
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_hide)
        )

    @hide.error
    async def hide_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

    @commands.command(name="unhide")
    @commands.has_permissions(manage_channels=True)
    async def unhide(self, ctx):

        async def do_unhide(interaction: discord.Interaction):

            overwrite = interaction.channel.overwrites_for(
                interaction.guild.default_role
            )

            overwrite.view_channel = None

            await interaction.channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite
            )

            embed = discord.Embed(
                description=f"<:check:1514888247401123923> {interaction.channel.mention} has been made visible.",
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description="Are you sure you want to unhide this channel?",
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_unhide)
        )

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        if member == ctx.author:
            return await ctx.send(
                embed=discord.Embed(
                    description="You cannot ban yourself.",
                    color=discord.Color.red()
                )
            )

        if member.top_role >= ctx.author.top_role:
            return await ctx.send(
                embed=discord.Embed(
                    description="You cannot ban a member with an equal or higher role.",
                    color=discord.Color.red()
                )
            )

        async def do_ban(interaction: discord.Interaction):

            await member.ban(reason=reason)

            embed = discord.Embed(
                description=f"<:check:1514888247401123923> Banned {member.mention}, reason: {reason}",
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description=f"Are you sure you want to ban {member.mention}, reason: {reason}?",
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_ban)
        )

    @ban.error
    async def ban_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description="Member not found.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.ban <member> [reason]`",
                    color=discord.Color.red()
                )
            )

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        ctx,
        user_id: int
    ):

        try:
            user = await self.bot.fetch_user(user_id)
        except:
            return await ctx.send(
                embed=discord.Embed(
                    description="User not found.",
                    color=discord.Color.red()
                )
            )

        async def do_unban(interaction: discord.Interaction):

            await ctx.guild.unban(user)

            embed = discord.Embed(
                description=f"<:check:1514888247401123923> Unbanned: {user.mention if hasattr(user, 'mention') else user}.",
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description=f"Are you sure you want to unban `{user}`?",
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_unban)
        )

    @unban.error
    async def unban_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.unban <user_id>`",
                    color=discord.Color.red()
                )
            )

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        if member == ctx.author:
            return await ctx.send(
                embed=discord.Embed(
                    description="You cannot kick yourself.",
                    color=discord.Color.red()
                )
            )

        if member.top_role >= ctx.author.top_role:
            return await ctx.send(
                embed=discord.Embed(
                    description="You cannot kick a member with an equal or higher role.",
                    color=discord.Color.red()
                )
            )

        async def do_kick(interaction: discord.Interaction):

            await member.kick(reason=reason)

            embed = discord.Embed(
                description=(
                    f"<:check:1514888247401123923> Kicked {member.mention}, reason: {reason}"
                ),
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description=(
                f"Are you sure you want to kick {member.mention}, reason: {reason} ?"
            ),
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_kick)
        )

    @kick.error
    async def kick_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description="Member not found.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.kick <member> [reason]`",
                    color=discord.Color.red()
                )
            )


    @commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(
        self,
        ctx,
        member: discord.Member,
        duration: int,
        *,
        reason: str = "No reason provided"
    ):

        if member == ctx.author:
            return await ctx.send(
                embed=discord.Embed(
                    description="You cannot timeout yourself.",
                    color=discord.Color.red()
                )
            )

        if member.top_role >= ctx.author.top_role:
            return await ctx.send(
                embed=discord.Embed(
                    description="You cannot timeout a member with an equal or higher role.",
                    color=discord.Color.red()
                )
            )

        async def do_timeout(interaction: discord.Interaction):

            await member.timeout(
                timedelta(minutes=duration),
                reason=reason
            )

            embed = discord.Embed(
                description=(
                    f"<:check:1514888247401123923> Muted {member.mention}, reason: {reason}, duration: {duration}"
                ),
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description=(
                f"Are you sure you want to timeout {member.mention}, reason: {reason}, duration: {duration}?"
            ),
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_timeout)
        )

    @mute.error
    async def mute_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description="Member not found.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.mute <member> <minutes> [reason]`",
                    color=discord.Color.red()
                )
            )

    @commands.command(
        name="unmute",
        aliases=["untimeout"]
    )
    @commands.has_permissions(moderate_members=True)
    async def unmute(
        self,
        ctx,
        member: discord.Member
    ):

        async def do_unmute(interaction: discord.Interaction):

            await member.timeout(
                None,
                reason=f"Timeout removed by {ctx.author}"
            )

            embed = discord.Embed(
                description=f"<:check:1514888247401123923> Unmuted {member.mention}",
                color=0xA3EB7B
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

        embed = discord.Embed(
            description=(
                f"Are you sure you want to remove the timeout from {member.mention}?"
            ),
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=ConfirmView(ctx.author.id, do_unmute)
        )

    @unmute.error
    async def unmute_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description="Member not found.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.unmute <member>`",
                    color=discord.Color.red()
                )
            )

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        if member == ctx.author:
            return await ctx.send(
                embed=discord.Embed(
                    description="You cannot warn yourself.",
                    color=discord.Color.red()
                )
            )

        try:
            with open("warnings.json", "r") as f:
                warnings = json.load(f)
        except:
            warnings = {}

        user_id = str(member.id)

        if user_id not in warnings:
            warnings[user_id] = []

        warnings[user_id].append({
            "moderator": ctx.author.id,
            "reason": reason,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })

        with open("warnings.json", "w") as f:
            json.dump(warnings, f, indent=4)

        warning_count = len(warnings[user_id])

        try:
            dm_embed = discord.Embed(
                description=(
                    f"You have been warned in **{ctx.guild.name}**.\n"
                    f"Reason: {reason}\n"
                    f"Total Warnings: {warning_count}"
                ),
                color=discord.Color.red()
            )

            await member.send(embed=dm_embed)

        except:
            pass

        embed = discord.Embed(
            description=(
                f"<:check:1514888247401123923> Warned {member.mention}, reason: {reason}, total warnings: {warning_count}"
            ),
            color=0xA3EB7B
        )

        await ctx.send(embed=embed)

    @warn.error
    async def warn_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description="Member not found.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.warn <member> <reason>`",
                    color=discord.Color.red()
                )
            )

    @commands.command(
        name="warnings",
        aliases=["warns"]
    )
    @commands.has_permissions(moderate_members=True)
    async def warnings(
        self,
        ctx,
        member: discord.Member
    ):

        try:
            with open("warnings.json", "r") as f:
                warnings = json.load(f)
        except:
            warnings = {}

        user_id = str(member.id)

        if user_id not in warnings or len(warnings[user_id]) == 0:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"{member.mention} has no warnings.",
                    color=0xFFFFFF
                )
            )

        embed = discord.Embed(
            title=f"Warnings for {member}",
            color=0xFFFFFF
        )

        for index, warning in enumerate(warnings[user_id], start=1):

            moderator = ctx.guild.get_member(
                warning["moderator"]
            )

            moderator_name = (
                moderator.mention
                if moderator
                else f"`{warning['moderator']}`"
            )

            embed.add_field(
                name=f"Warning #{index}",
                value=(
                    f"**Reason:** {warning['reason']}\n"
                    f"**Moderator:** {moderator_name}\n"
                    f"**Date:** {warning['timestamp']}"
                ),
                inline=False
            )

        embed.set_footer(
            text=f"Total Warnings: {len(warnings[user_id])}"
        )

        await ctx.send(embed=embed)

    @warnings.error
    async def warnings_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description="Member not found.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.warnings <member>`",
                    color=discord.Color.red()
                )
            )

    @commands.command(
        name="clearwarns",
        aliases=["resetwarns"]
    )
    @commands.has_permissions(manage_messages=True)
    async def clearwarns(
        self,
        ctx,
        member: discord.Member
    ):

        try:
            with open("warnings.json", "r") as f:
                warnings = json.load(f)
        except:
            warnings = {}

        user_id = str(member.id)

        if user_id not in warnings or len(warnings[user_id]) == 0:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"{member.mention} has no warnings.",
                    color=discord.Color.red()
                )
            )

        amount = len(warnings[user_id])

        del warnings[user_id]

        with open("warnings.json", "w") as f:
            json.dump(warnings, f, indent=4)

        try:
            await member.send(
                embed=discord.Embed(
                    description=(
                        f"Your warning history has been cleared in "
                        f"**{ctx.guild.name}**."
                    ),
                    color=0xA3EB7B
                )
            )
        except:
            pass

        await ctx.send(
            embed=discord.Embed(
                description=(
                    f"Removed Warnings for {member.mention}, removed warnings: {amount}"
                ),
                color=0xFFFFFF
            )
        )

    @clearwarns.error
    async def clearwarns_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="You do not have permission to use this command.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description="Member not found.",
                    color=discord.Color.red()
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="Usage: `.clearwarns <member>`",
                    color=discord.Color.red()
                )
            )

async def setup(bot):
    await bot.add_cog(Moderation(bot))