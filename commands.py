import datetime
import discord
from discord.ext import commands
from discord import app_commands

import wack
from gpt_utils import clear_history


class BotCommands(commands.Cog):
    """All of Mepl's slash commands: chat/config utilities and moderation."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

    # --- Utility ---

    @app_commands.command(name='ping', description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Pong! {round(self.bot.latency * 1000)}ms')

    @app_commands.command(name='uptime', description='Show how long the bot has been running')
    async def uptime(self, interaction: discord.Interaction):
        delta = datetime.datetime.now(datetime.timezone.utc) - self.start_time
        days, remainder = divmod(int(delta.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")

        await interaction.response.send_message(f"I've been up for {' '.join(parts)}.", ephemeral=True)

    @app_commands.command(name='wack', description='Reload the bot configuration from disk (admin only)')
    @app_commands.checks.has_permissions(administrator=True)
    async def wack(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # Hold the response first, give a "thinking..." animation
        async with wack.config_lock:
            wack.reload_config()
        await interaction.followup.send("Uhh.. my head hurt 🤕 (config reloaded)", ephemeral=True)

    @app_commands.command(name='help', description='Show the bot command list')
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Mepl — Command List",
            description="Mention me or chat in a registered channel and I'll talk back naturally. Here's everything else I can do:",
            color=discord.Color.blurple()
        )
        if self.bot.user and self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="💬 Chat",
            value=(
                "`/register` — Always reply in this channel\n"
                "`/unregister` — Stop always-replying here\n"
                "`/reset` — Forget this channel's conversation so far\n"
                "`/language <language>` — Set my reply language for this server"
            ),
            inline=False
        )
        embed.add_field(
            name="🛠️ Utility",
            value=(
                "`/help` — Show this list\n"
                "`/ping` — Check my latency\n"
                "`/uptime` — See how long I've been running\n"
                "`/wack` — Reload my config from disk (admin only)"
            ),
            inline=False
        )
        embed.add_field(
            name="🛡️ Moderation",
            value=(
                "`/kick` — Kick a member\n"
                "`/ban` — Ban a member\n"
                "`/timeout` — Timeout a member\n"
                "`/purge <amount>` — Delete multiple messages"
            ),
            inline=False
        )
        embed.set_footer(text=f"I'll also randomly jump into unregistered channels about {int(wack.RANDOM_CHAT_CHANCE * 100)}% of the time.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Chat / config ---

    @app_commands.command(name='register', description='Register the current channel for always-on bot replies')
    async def register(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
            return

        async with wack.config_lock:
            newly_registered = wack.register_channel(str(interaction.guild.id), str(interaction.channel.id))

        if newly_registered:
            await interaction.response.send_message('This channel has been registered to the database.')
        else:
            await interaction.response.send_message('This channel is already registered.')

    @app_commands.command(name='unregister', description='Remove the current channel from always-on bot replies')
    async def unregister(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
            return

        async with wack.config_lock:
            was_registered = wack.unregister_channel(str(interaction.guild.id), str(interaction.channel.id))

        if was_registered:
            await interaction.response.send_message('This channel has been removed from the database.')
        else:
            await interaction.response.send_message('This channel is not registered in the database.')

    @app_commands.command(name='language', description='Set the bot response language for this server')
    async def language(self, interaction: discord.Interaction, language: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
            return

        clean_language = language.strip()
        if not clean_language:
            await interaction.response.send_message("Please provide an actual language, like `English` or `Indonesian`.", ephemeral=True)
            return

        async with wack.config_lock:
            wack.set_language(str(interaction.guild.id), clean_language)

        await interaction.response.send_message(
            f'Bot response language set to `{clean_language}` for this server.',
            ephemeral=True
        )

    @app_commands.command(name='reset', description="Make the bot forget this channel's conversation so far")
    async def reset(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
            return

        conversation_id = f'{interaction.guild.id}-{interaction.channel.id}'
        cleared = clear_history(conversation_id)

        if cleared:
            await interaction.response.send_message("Alright, clean slate — I forgot our conversation here.", ephemeral=True)
        else:
            await interaction.response.send_message("There's nothing to forget yet in this channel.", ephemeral=True)

    # --- Moderation ---

    @app_commands.command(name="kick", description="Kicks a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"{member.display_name} has been kicked. Reason: {reason or 'No reason provided'}"
        )

    @app_commands.command(name="ban", description="Bans a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await member.ban(reason=reason)
        await interaction.response.send_message(
            f"{member.display_name} has been banned. Reason: {reason or 'No reason provided'}"
        )

    @app_commands.command(name="timeout", description="Timeouts a member")
    @app_commands.describe(member="Member to timeout", duration="Duration in seconds (max 28 days)", reason="Reason for timeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = None):
        if duration < 1:
            await interaction.response.send_message("Duration must be at least 1 second!", ephemeral=True)
            return

        duration = min(duration, 2419200)  # cap at 28 days
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=duration), reason=reason)
        await interaction.response.send_message(
            f"{member.display_name} has been timed out for {duration} seconds. Reason: {reason or 'No reason provided'}"
        )

    @app_commands.command(name="purge", description="Delete multiple messages at once")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("Amount must be between 1-100!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        # No `+1` here: unlike a prefix command, a slash command doesn't post its own
        # message in the channel, so there's nothing extra to account for.
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages", ephemeral=True)


# --- Centralized error handling for all slash commands ---
# Avoids repeating try/except blocks in every command and makes sure the user
# always gets a readable message instead of Discord's generic "interaction failed".
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    original = getattr(error, 'original', error)

    if isinstance(error, app_commands.MissingPermissions):
        message = "You don't have permission to use this command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        message = "I don't have the permissions I need to do that."
    elif isinstance(error, app_commands.CommandOnCooldown):
        message = f"Slow down a bit! Try again in {error.retry_after:.1f}s."
    elif isinstance(original, discord.Forbidden):
        message = "I don't have permission to do that."
    else:
        print(f"Unhandled app command error in /{interaction.command.name if interaction.command else '?'}: {error}")
        message = "Something went wrong running that command."

    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException:
        pass


async def setup(bot: commands.Bot):
    bot.tree.on_error = on_app_command_error
    await bot.add_cog(BotCommands(bot))
