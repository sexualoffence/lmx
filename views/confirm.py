import discord

class ConfirmView(discord.ui.View):
    def __init__(self, author_id, yes_callback):
        super().__init__(timeout=30)
        self.author_id = author_id
        self.yes_callback = yes_callback

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot use these buttons.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.secondary)
    async def yes(self, interaction, button):
        await self.yes_callback(interaction)
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def no(self, interaction, button):
        await interaction.response.edit_message(
            content="Cancelled.",
            view=None
        )
        self.stop()