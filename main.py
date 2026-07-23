import os
import discord
import json
import datetime
import random
import asyncio
from gpt_utils import gpt_response, clear_history
from keep_alive import keep_alive
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

keep_alive()
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise RuntimeError('DISCORD_TOKEN is not set. Please add it to your .env file or environment variables.')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # needed for kick/ban/timeout targets

bot = commands.Bot(command_prefix='!', intents=intents)
START_TIME = datetime.datetime.now(datetime.timezone.utc)

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        return {}

    for guild_id, guild_data in list(config.items()):
        if isinstance(guild_data, list):
            config[guild_id] = {"channels": guild_data}
        elif isinstance(guild_data, dict) and "channels" not in guild_data:
            config[guild_id] = {"channels": guild_data.get("channels", []), "language": guild_data.get("language")}
    return config

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

MAX_DISCORD_MESSAGE_LENGTH = 2000
RANDOM_CHAT_CHANCE = 0.2

def split_message(text, limit=MAX_DISCORD_MESSAGE_LENGTH):
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break

        split_at = text.rfind('\n', 0, limit)
        if split_at == -1:
            split_at = text.rfind(' ', 0, limit)
        if split_at == -1:
            split_at = limit

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()

    return chunks

async def send_long_message(channel, content):
    if content is None:
        return
    for chunk in split_message(str(content)):
        if chunk:
            await channel.send(chunk)

# Load awal untuk dipakai on_message
config = load_config()
# Guards read-modify-write access to `config` so concurrent slash commands
# (e.g. from two different servers at once) can't clobber each other's changes.
config_lock = asyncio.Lock()


def get_guild_language(guild_id):
    guild_config = config.get(guild_id)
    if isinstance(guild_config, dict):
        return guild_config.get("language")
    return None

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='IamMepl'))
    print(f'{bot.user.name} online!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return

    if message.guild is None:
        return

    guild_id = str(message.guild.id)
    channel_id = str(message.channel.id)

    is_registered_channel = guild_id in config and channel_id in config[guild_id].get("channels", [])
    mention = bot.user.mentioned_in(message)
    should_random_reply = not is_registered_channel and random.random() < RANDOM_CHAT_CHANCE

    image_urls = [attachment.url for attachment in message.attachments if not attachment.content_type or attachment.content_type.startswith('image')]

    if is_registered_channel or mention or should_random_reply:
        async with message.channel.typing():
            delay = random.uniform(1.5, 3.0)  # Random between 1.5 to 3 seconds
            await asyncio.sleep(delay)
            content = message.content
            if mention:
                content = message.content.replace(f'<@{bot.user.id}>', '').strip()
            conversation_id = f'{guild_id}-{channel_id}'
            await send_long_message(
                message.channel,
                gpt_response(
                    content,
                    get_guild_language(guild_id),
                    image_urls=image_urls,
                    conversation_id=conversation_id,
                    author_name=message.author.display_name
                )
            )

    await bot.process_commands(message)

@bot.tree.error
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

@bot.tree.command(name='ping', description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'Pong! {round(bot.latency * 1000)}ms')

@bot.tree.command(name='uptime', description='Show how long the bot has been running')
async def uptime(interaction: discord.Interaction):
    delta = datetime.datetime.now(datetime.timezone.utc) - START_TIME
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

@bot.tree.command(name='wack', description='Reload the bot configuration from disk (admin only)')
@app_commands.checks.has_permissions(administrator=True)
async def reloadconfig(interaction: discord.Interaction):
    global config
    await interaction.response.defer(ephemeral=True)  # Hold the response first, give a "thinking..." animation
    async with config_lock:
        config = load_config()
    await asyncio.sleep(1.5)
    await interaction.followup.send("Uhh.. my head hurt 🤕 (config reloaded)", ephemeral=True)

@bot.tree.command(name='register', description='Register the current channel for always-on bot replies')
async def register(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
        return

    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    async with config_lock:
        if guild_id not in config or not isinstance(config[guild_id], dict):
            config[guild_id] = {"channels": []}

        already_registered = channel_id in config[guild_id]["channels"]
        if not already_registered:
            config[guild_id]["channels"].append(channel_id)
            save_config(config)

    if already_registered:
        await interaction.response.send_message('This channel is already registered.')
    else:
        await interaction.response.send_message('This channel has been registered to the database.')

@bot.tree.command(name='unregister', description='Remove the current channel from always-on bot replies')
async def unregister(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
        return

    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    async with config_lock:
        was_registered = guild_id in config and channel_id in config[guild_id].get("channels", [])
        if was_registered:
            config[guild_id]["channels"].remove(channel_id)
            save_config(config)

    if was_registered:
        await interaction.response.send_message('This channel has been removed from the database.')
    else:
        await interaction.response.send_message('This channel is not registered in the database.')

@bot.tree.command(name='language', description='Set the bot response language for this server')
async def language(interaction: discord.Interaction, language: str):
    if interaction.guild is None:
        await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
        return

    clean_language = language.strip()
    if not clean_language:
        await interaction.response.send_message("Please provide an actual language, like `English` or `Indonesian`.", ephemeral=True)
        return

    guild_id = str(interaction.guild.id)

    async with config_lock:
        if guild_id not in config or not isinstance(config[guild_id], dict):
            config[guild_id] = {"channels": []}
        config[guild_id]["language"] = clean_language
        save_config(config)

    await interaction.response.send_message(
        f'Bot response language set to `{clean_language}` for this server.',
        ephemeral=True
    )

@bot.tree.command(name='reset', description="Make the bot forget this channel's conversation so far")
async def reset(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("This command only works inside a server.", ephemeral=True)
        return

    conversation_id = f'{interaction.guild.id}-{interaction.channel.id}'
    cleared = clear_history(conversation_id)

    if cleared:
        await interaction.response.send_message("Alright, clean slate — I forgot our conversation here.", ephemeral=True)
    else:
        await interaction.response.send_message("There's nothing to forget yet in this channel.", ephemeral=True)

@bot.tree.command(name='help', description='Show the bot command list')
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Mepl — Command List",
        description="Mention me or chat in a registered channel and I'll talk back naturally. Here's everything else I can do:",
        color=discord.Color.blurple()
    )
    if bot.user and bot.user.display_avatar:
        embed.set_thumbnail(url=bot.user.display_avatar.url)

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
    embed.set_footer(text=f"I'll also randomly jump into unregistered channels about {int(RANDOM_CHAT_CHANCE * 100)}% of the time.")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="kick", description="Kicks a member from the server")
@app_commands.describe(member="Member to kick", reason="Reason for kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(
        f"{member.display_name} has been kicked. Reason: {reason or 'No reason provided'}"
    )

@bot.tree.command(name="ban", description="Bans a member from the server")
@app_commands.describe(member="Member to ban", reason="Reason for ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(
        f"{member.display_name} has been banned. Reason: {reason or 'No reason provided'}"
    )

@bot.tree.command(name="timeout", description="Timeouts a member")
@app_commands.describe(member="Member to timeout", duration="Duration in seconds (max 28 days)", reason="Reason for timeout")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = None):
    if duration < 1:
        await interaction.response.send_message("Duration must be at least 1 second!", ephemeral=True)
        return

    duration = min(duration, 2419200)  # cap at 28 days
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=duration), reason=reason)
    await interaction.response.send_message(
        f"{member.display_name} has been timed out for {duration} seconds. Reason: {reason or 'No reason provided'}"
    )

@bot.tree.command(name="purge", description="Delete multiple messages at once")
@app_commands.describe(amount="Number of messages to delete (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("Amount must be between 1-100!", ephemeral=True)
        return

    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Deleted {len(deleted)} messages", ephemeral=True)

bot.run(TOKEN)
