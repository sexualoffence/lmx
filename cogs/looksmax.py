import os
import json
import time
import discord
from discord.ext import commands

APPROVED_USERS = {
    1405921081138745364,
    1512834394900136189,
    1259551720325779540
}

REVIEW_CHANNEL_ID = 1514236624718921738
REVIEW_PINGS = [
    1512834394900136189,
    1405921081138745364,
    1259551720325779540
]


def error_embed(message: str):
    return discord.Embed(
        description=message,
        color=discord.Color.red()
    )


REJECT_REASONS = [
    "Face doesn't match",
    "Upload your own photo",
    "Photo is not clear enough",
    "Filters detected",
    "Additional lighting detected",
    "AI-generated image detected",
]


class RejectModal(discord.ui.Modal, title="Custom Rejection Reason"):
    reason = discord.ui.TextInput(
        label="Reason",
        style=discord.TextStyle.paragraph,
        placeholder="Enter the rejection reason...",
        required=True,
        max_length=1000
    )

    def __init__(self, submitter_id: int):
        super().__init__()
        self.submitter_id = submitter_id

    async def on_submit(self, interaction: discord.Interaction):
        await _send_rejection(interaction, self.submitter_id, self.reason.value)


async def _send_rejection(interaction: discord.Interaction, submitter_id: int, reason: str):
    try:
        user = await interaction.client.fetch_user(submitter_id)
        await user.send(
            embed=discord.Embed(
                description=f"Your ranking submission was rejected.\n\n**Reason:** {reason}",
                color=discord.Color.red()
            )
        )
    except discord.HTTPException:
        pass

    await interaction.message.edit(view=None)
    await interaction.response.send_message(
        embed=discord.Embed(
            description="Submission rejected. User notified.",
            color=discord.Color.red()
        ),
        ephemeral=True
    )


class RejectView(discord.ui.View):
    def __init__(self, submitter_id: int):
        super().__init__(timeout=None)
        self.submitter_id = submitter_id

    @discord.ui.button(label="Face doesn't match", style=discord.ButtonStyle.danger, row=0)
    async def face_mismatch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _send_rejection(interaction, self.submitter_id, "Face doesn't match")

    @discord.ui.button(label="Upload your own photo", style=discord.ButtonStyle.danger, row=0)
    async def upload_own(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _send_rejection(interaction, self.submitter_id, "Upload your own photo")

    @discord.ui.button(label="Not clear enough", style=discord.ButtonStyle.danger, row=0)
    async def not_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _send_rejection(interaction, self.submitter_id, "Photo is not clear enough")

    @discord.ui.button(label="Filters detected", style=discord.ButtonStyle.danger, row=1)
    async def filters(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _send_rejection(interaction, self.submitter_id, "Filters detected")

    @discord.ui.button(label="Lighting detected", style=discord.ButtonStyle.danger, row=1)
    async def lighting(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _send_rejection(interaction, self.submitter_id, "Additional lighting detected")

    @discord.ui.button(label="AI-generated", style=discord.ButtonStyle.danger, row=1)
    async def ai_generated(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _send_rejection(interaction, self.submitter_id, "AI-generated image detected")

    @discord.ui.button(label="Custom", style=discord.ButtonStyle.secondary, row=2)
    async def custom(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RejectModal(submitter_id=self.submitter_id)
        await interaction.response.send_modal(modal)


class RankView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Get Ranked",
        emoji="<:Rank:1514888032854085662>",
        style=discord.ButtonStyle.secondary,
        custom_id="get_ranked"
    )
    async def get_ranked(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        user_id = str(interaction.user.id)
        data = load_submissions()
        entry = data.get(user_id)

        if entry and interaction.user.id not in APPROVED_USERS:
            if entry["attempts"] >= MAX_ATTEMPTS:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        description="You've used all **3 attempts**. You can no longer submit for ranking.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            if entry["last_ranked"]:
                elapsed = time.time() - entry["last_ranked"]
                if elapsed < COOLDOWN_DAYS * 86400:
                    remaining = int(COOLDOWN_DAYS - elapsed / 86400)
                    return await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"You were already ranked. You can submit again in **{remaining} day(s)**.",
                            color=discord.Color.red()
                        ),
                        ephemeral=True
                    )

        embed = discord.Embed(
            description=(
                "**To proceed with your submission, please upload exactly 2 photos:**\n"
                "<:one_one:1514898068858736750> Front profile photo\n"
                "<:two_two:1514898242590998539> Side profile photo\n\n"
                "**Requirements:**\n"
                "<:dots:1514900102471225365> Photo must be yourself\n"
                "<:dots:1514900102471225365> No filters\n"
                "<:dots:1514900102471225365> No additional lighting\n\n"
                "Submissions containing someone else's photos, AI-generated images, or images that do not meet these requirements may be rejected."
            ),
            color=0xFFFFFF
        )

        await interaction.response.send_message(
            embed=discord.Embed(
                description="<:check:1514888247401123923> Check your DMs.",
                color=0xA3EB7B
            ),
            ephemeral=True
        )

        try:
            await interaction.user.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            return await interaction.followup.send(
                embed=discord.Embed(
                    description="I couldn't DM you. Please enable DMs and try again.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        cog = interaction.client.get_cog("LooksMax")
        if cog:
            cog.active_submissions.add(interaction.user.id)


ROLE_IDS = {
    "sub3": 0,
    "sub5": 0,
    "LTN": 1514227142609731705,
    "MTN": 1514227187144720564,
    "HTN": 1514227229872230525,
    "LTB": 0,
    "MTB": 0,
    "HTB": 0,
    "CL": 0,
    "Chad": 0,
    "Stacylite": 0,
    "Stacy": 0,
}

SUBMISSIONS_FILE = "submissions.json"
MAX_ATTEMPTS = 3
COOLDOWN_DAYS = 30


def load_submissions():
    if not os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "w") as f:
            json.dump({}, f)
    with open(SUBMISSIONS_FILE, "r") as f:
        return json.load(f)


def save_submissions(data):
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)


class RoleView(discord.ui.View):
    def __init__(self, submitter_id: int, submitter_guild_id: int):
        super().__init__(timeout=None)
        self.submitter_id = submitter_id
        self.submitter_guild_id = submitter_guild_id

    @discord.ui.button(label="sub3", style=discord.ButtonStyle.secondary)
    async def sub3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "sub3")

    @discord.ui.button(label="sub5", style=discord.ButtonStyle.secondary)
    async def sub5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "sub5")

    @discord.ui.button(label="LTN", style=discord.ButtonStyle.secondary)
    async def ltn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "LTN")

    @discord.ui.button(label="MTN", style=discord.ButtonStyle.secondary)
    async def mtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "MTN")

    @discord.ui.button(label="HTN", style=discord.ButtonStyle.secondary)
    async def htn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "HTN")

    @discord.ui.button(label="LTB", style=discord.ButtonStyle.secondary)
    async def ltb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "LTB")

    @discord.ui.button(label="MTB", style=discord.ButtonStyle.secondary)
    async def mtb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "MTB")

    @discord.ui.button(label="HTB", style=discord.ButtonStyle.secondary)
    async def htb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "HTB")

    @discord.ui.button(label="CL", style=discord.ButtonStyle.secondary)
    async def cl(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "CL")

    @discord.ui.button(label="Chad", style=discord.ButtonStyle.secondary)
    async def chad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "Chad")

    @discord.ui.button(label="Stacylite", style=discord.ButtonStyle.secondary)
    async def stacylite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "Stacylite")

    @discord.ui.button(label="Stacy", style=discord.ButtonStyle.secondary)
    async def stacy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._assign_role(interaction, "Stacy")

    async def _assign_role(self, interaction: discord.Interaction, tier: str):
        guild = interaction.client.get_guild(self.submitter_guild_id)
        if guild is None:
            return await interaction.response.send_message("Guild not found.", ephemeral=True)

        role_id = ROLE_IDS[tier]
        if not role_id:
            return await interaction.response.send_message(
                f"Role ID for {tier} is not set in config.", ephemeral=True
            )

        role = guild.get_role(role_id)
        if role is None:
            return await interaction.response.send_message(f"Role `{tier}` not found.", ephemeral=True)

        member = guild.get_member(self.submitter_id)
        if member is None:
            return await interaction.response.send_message("User is not in this server.", ephemeral=True)

        old_roles = [guild.get_role(rid) for rid in ROLE_IDS.values() if guild.get_role(rid) in member.roles]

        try:
            if old_roles:
                await member.remove_roles(*old_roles)
            await member.add_roles(role)
        except discord.Forbidden:
            return await interaction.response.send_message(
                "I don't have permission to manage roles.", ephemeral=True
            )

        try:
            user = await interaction.client.fetch_user(self.submitter_id)
            await user.send(
                embed=discord.Embed(
                    description=f"<:check:1514888247401123923> Your ranking submission has been approved!\n\n**Tier:** {tier}",
                    color=0xA3EB7B
                )
            )
        except discord.HTTPException:
            pass

        user_id = str(self.submitter_id)
        data = load_submissions()
        entry = data.get(user_id, {"name": "", "attempts": 0, "last_ranked": None, "last_tier": None})
        entry["last_ranked"] = time.time()
        entry["last_tier"] = tier
        data[user_id] = entry
        save_submissions(data)

        await interaction.message.edit(view=None)
        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"Assigned **{tier}** to <@{self.submitter_id}>.",
                color=0xA3EB7B
            ),
            ephemeral=True
        )


class ReviewView(discord.ui.View):
    def __init__(self, submitter_id: int, submitter_guild_id: int):
        super().__init__(timeout=None)
        self.submitter_id = submitter_id
        self.submitter_guild_id = submitter_guild_id

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(
            view=RoleView(
                submitter_id=self.submitter_id,
                submitter_guild_id=self.submitter_guild_id
            )
        )
        await interaction.response.send_message(
            embed=discord.Embed(
                description="Select a tier to assign.",
                color=discord.Color.blurple()
            ),
            ephemeral=True
        )

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(
            view=RejectView(submitter_id=self.submitter_id)
        )
        await interaction.response.send_message(
            embed=discord.Embed(
                description="Select a rejection reason.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )


class LooksMax(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_submissions = set()

    @commands.command(name="setuprank")
    async def setuprank(self, ctx):

        if ctx.author.id not in APPROVED_USERS:
            return await ctx.send(
                embed=error_embed(
                    "You are not authorized to use this command."
                )
            )

        embed = discord.Embed(
            title="Whats this ?",
            description="This is our ranking system, where your facial features and overall presentation are reviewed by our analysis team, To participate, submit the required photos and wait for your review. Once your submission has been processed, you will receive your assigned rank.",
            color=0xFFFFFF
        )

        await ctx.send(
            embed=embed,
            view=RankView()
        )

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not isinstance(message.channel, discord.DMChannel):
            return

        if message.author.id not in self.active_submissions:
            return

        if not message.attachments:
            return

        if len(message.attachments) != 2:
            await message.channel.send(
                embed=discord.Embed(
                    description="Please send exactly **2 photos**:\n<:one_one:1514898068858736750> Front profile\n<:two_two:1514898242590998539> Side profile",
                    color=discord.Color.red()
                )
            )
            return

        for attachment in message.attachments:
            if not attachment.content_type or not attachment.content_type.startswith("image/"):
                await message.channel.send(
                    embed=discord.Embed(
                        description="Please send only image files (PNG, JPG, etc.).",
                        color=0xFFFFFF
                    )
                )
                return

        review_channel = self.bot.get_channel(REVIEW_CHANNEL_ID)

        if review_channel is None:
            return

        info_embed = discord.Embed(
            title="New Submission",
            description=(
                f"User: {message.author.mention}\n"
                f"Username: {message.author}\n"
                f"User ID: `{message.author.id}`"
            ),
            color=0xFFFFFF
        )

        files = []
        photo_embeds = []
        labels = ["Front Profile", "Side Profile"]

        for i, (attachment, label) in enumerate(zip(message.attachments, labels)):
            try:
                ext = os.path.splitext(attachment.filename)[1] or ".jpg"
                file = await attachment.to_file(filename=f"submission_{i}{ext}")
                files.append(file)
                photo_embed = discord.Embed(title=label, color=0xFFFFFF)
                photo_embed.set_image(url=f"attachment://submission_{i}{ext}")
                photo_embeds.append(photo_embed)
            except Exception:
                pass

        ping_content = " ".join(f"<@{uid}>" for uid in REVIEW_PINGS) if REVIEW_PINGS else None

        msg = await review_channel.send(
            content=ping_content,
            embeds=[info_embed, *photo_embeds],
            files=files,
            view=ReviewView(
                submitter_id=message.author.id,
                submitter_guild_id=review_channel.guild.id
            )
        )

        self.active_submissions.discard(message.author.id)

        user_id = str(message.author.id)
        data = load_submissions()
        entry = data.get(user_id, {"name": str(message.author), "attempts": 0, "last_ranked": None, "last_tier": None})
        entry["name"] = str(message.author)
        entry["attempts"] += 1
        data[user_id] = entry
        save_submissions(data)

        await message.channel.send(
            embed=discord.Embed(
                description="<:check:1514888247401123923> Your photos are under review ",
                color=0xA3EB7B
            )
        )


async def setup(bot):
    await bot.add_cog(LooksMax(bot))