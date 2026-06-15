import json
import discord
from discord.ext import commands

class AvatarView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=60)
        self.member = member

        if member.guild_avatar is None:
            self.server_avatar.disabled = True

    @discord.ui.button(
        label="Global Avatar",
        style=discord.ButtonStyle.secondary
    )
    async def global_avatar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        embed = discord.Embed(
            title=f"{self.member.display_name}'s Global Avatar",
            color=0xFFFFFF
        )

        embed.set_image(url=self.member.display_avatar.url)

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="Server Avatar",
        style=discord.ButtonStyle.secondary
    )
    async def server_avatar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        embed = discord.Embed(
            title=f"{self.member.display_name}'s Server Avatar",
            color=0xFFFFFF
        )

        embed.set_image(url=self.member.guild_avatar.url)

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="setup",
        invoke_without_command=True
    )
    async def setup(self, ctx):

        embed = discord.Embed(
            title="Setup Commands",
            description="Available Commands:\n\n`.setup jail <role>`",
            color=0xFFFFFF
        )

        await ctx.send(embed=embed)

    @setup.command(name="jail")
    @commands.has_permissions(administrator=True)
    async def setup_jail(
        self,
        ctx,
        jail_role: discord.Role
    ):

        try:
            with open("jail.json", "r") as f:
                data = json.load(f)
        except:
            data = {}

        guild_id = str(ctx.guild.id)

        data[guild_id] = {
            "role": jail_role.id
        }

        with open("jail.json", "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            description=f"<:check:1514888247401123923> Jail role set to {jail_role.mention}.",
            color=0xA3EB7B
        )

        await ctx.send(embed=embed)

    @commands.command(
            name="jail",
            aliases=["sentence"]
            )
    @commands.has_permissions(moderate_members=True)
    async def jail(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        try:
            with open("jail.json", "r") as f:
                data = json.load(f)
        except:
            data = {}

        guild_id = str(ctx.guild.id)

        if guild_id not in data:
            return await ctx.send(
                embed=discord.Embed(
                    description="Jail role has not been configured. Use `.setup jail <role>` first.",
                    color=discord.Color.red()
                )
            )

        role = ctx.guild.get_role(
            data[guild_id]["role"]
        )

        if role is None:
            return await ctx.send(
                embed=discord.Embed(
                    description="Configured jail role no longer exists.",
                    color=discord.Color.red()
                )
            )

        await member.add_roles(role)

        try:
            await member.send(
                embed=discord.Embed(
                    description=(
                        f"You have been jailed in **{ctx.guild.name}**.\n"
                        f"Reason: {reason}"
                    ),
                    color=discord.Color.red()
                )
            )
        except:
            pass

        await ctx.send(
            embed=discord.Embed(
                description=f"<:check:1514888247401123923> jailed {member.mention}, reason: {reason}",
                color=0xA3EB7B
            )
        )

    @commands.command(name="unjail")
    @commands.has_permissions(moderate_members=True)
    async def unjail(
        self,
        ctx,
        member: discord.Member
    ):

        try:
            with open("jail.json", "r") as f:
                data = json.load(f)
        except:
            data = {}

        guild_id = str(ctx.guild.id)

        if guild_id not in data:
            return await ctx.send(
                embed=discord.Embed(
                    description="Jail role has not been configured.",
                    color=discord.Color.red()
                )
            )

        role = ctx.guild.get_role(
            data[guild_id]["role"]
        )

        if role is None:
            return await ctx.send(
                embed=discord.Embed(
                    description="Configured jail role no longer exists.",
                    color=discord.Color.red()
                )
            )

        if role not in member.roles:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"{member.mention} is not jailed.",
                    color=discord.Color.red()
                )
            )

        await member.remove_roles(role)

        try:
            await member.send(
                embed=discord.Embed(
                    description=(
                        f"You have been released from jail in **{ctx.guild.name}**."
                    ),
                    color=0xFFFFFF
                )
            )
        except:
            pass

        await ctx.send(
            embed=discord.Embed(
                description=f"<:check:1514888247401123923> unjailed {member.mention}",
                color=0xA3EB7B
            )
        )

    @unjail.error
    async def unjail_error(self, ctx, error):

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
                    description="Usage: `.unjail <member>`",
                    color=discord.Color.red()
                )
            )

    @commands.command(
        name="avatar",
        aliases=["av", "pfp"]
    )
    async def avatar(
        self,
        ctx,
        user: str = None
    ):

        if user is None:
            member = ctx.author

        else:
            try:
                member = await commands.MemberConverter().convert(
                    ctx,
                    user
                )

            except commands.MemberNotFound:

                try:
                    member = await self.bot.fetch_user(
                        int(user)
                    )

                except:
                    return await ctx.send(
                        embed=discord.Embed(
                            description="User not found.",
                            color=discord.Color.red()
                        )
                    )

        embed = discord.Embed(
            title=f"{member.display_name if hasattr(member, 'display_name') else member.name}'s Avatar",
            color=0xFFFFFF
        )

        embed.set_image(
            url=member.display_avatar.url
        )

        await ctx.send(
            embed=embed,
            view=AvatarView(member)
        )

    @avatar.error
    async def avatar_error(self, ctx, error):

        if isinstance(error, commands.BadArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="User not found.",
                    color=discord.Color.red()
                )
            )

    @commands.command(
        name="banner",
        aliases=["bnr"]
    )
    async def banner(
        self,
        ctx,
        user: str = None
    ):

        if user is None:
            target = ctx.author

        else:
            try:
                target = await commands.MemberConverter().convert(
                    ctx,
                    user
                )

            except commands.MemberNotFound:

                try:
                    target = await self.bot.fetch_user(
                        int(user)
                    )

                except:
                    return await ctx.send(
                        embed=discord.Embed(
                            description="User not found.",
                            color=discord.Color.red()
                        )
                    )

        user_obj = await self.bot.fetch_user(target.id)

        if user_obj.banner is None:
            return await ctx.send(
                embed=discord.Embed(
                    description="This user does not have a banner.",
                    color=discord.Color.red()
                )
            )

        embed = discord.Embed(
            title=f"{user_obj.name}'s Banner",
            color=0xFFFFFF
        )

        embed.set_image(
            url=user_obj.banner.url
        )

        await ctx.send(embed=embed)

    @banner.error
    async def banner_error(self, ctx, error):

        if isinstance(error, commands.BadArgument):
            await ctx.send(
                embed=discord.Embed(
                    description="User not found.",
                    color=discord.Color.red()
                )
            )

async def setup(bot):
    await bot.add_cog(Server(bot))