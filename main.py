import os
import discord
import threading
import time
import json
import datetime
import random
import asyncio
from gpt_utils import gpt_response
from keep_alive import keep_alive
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

keep_alive()
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # slash command

bot = commands.Bot(command_prefix='!', intents=intents)

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

# Load awal untuk dipakai on_message
config = load_config()

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
    if message.author == bot.user:
        return

    guild_id = str(message.guild.id)
    channel_id = str(message.channel.id)
    responded = False

    if guild_id in config and channel_id in config[guild_id]:
        async with message.channel.typing():
            delay = random.uniform(1.5, 3.0)  # Random between 1.5 to 3 seconds
            await asyncio.sleep(delay)
            await message.channel.send(gpt_response(message.content))
        responded = True

    if bot.user.mentioned_in(message) and not responded:
        async with message.channel.typing():
            delay = random.uniform(1.5, 3.0)
            await asyncio.sleep(delay)
            await message.channel.send(gpt_response(message.content.replace(f'<@{bot.user.id}>', '').strip()))
        responded = True
        
    await bot.process_commands(message)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    
@bot.tree.command(name='wack', description='To reload new data')
@commands.has_permissions(administrator=True)
async def reloadconfig(interaction: discord.Interaction):
    global config
    config = load_config()

    await interaction.response.defer(ephemeral=True)  # Hold the response first, give a "thinking..." animation
    await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=2))  # Delay 2 seconds 
    await interaction.followup.send("Uhh.. my head hurt 🤕", ephemeral=True)

@bot.tree.command(name='register', description='Register your channel id to database')
async def register(interaction: discord.Interaction):
    config = load_config()
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    if guild_id not in config:
        config[guild_id] = []

    if channel_id not in config[guild_id]:
        config[guild_id].append(channel_id)
        save_config(config)
        await interaction.response.send_message('This channel has been registered to the database.')
    else:
        await interaction.response.send_message('This channel is already registered.')

@bot.tree.command(name='unregister', description='Remove your channel id from database')
async def unregister(interaction: discord.Interaction):
    config = load_config()
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    if guild_id in config and channel_id in config[guild_id]:
        config[guild_id].remove(channel_id)
        save_config(config)
        await interaction.response.send_message('This channel has been removed from the database.')
    else:
        await interaction.response.send_message('This channel is not registered in the database.')

@bot.tree.command(name="kick", description="Kicks a member from the server")
@app_commands.describe(member="Member to kick", reason="Reason for kick")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("You don't have permission to kick members!", ephemeral=True)
            return

        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"{member.display_name} has been kicked. Reason: {reason or 'No reason provided'}"
        )
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to kick that member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="ban", description="Bans a member from the server")
@app_commands.describe(member="Member to ban", reason="Reason for ban")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("You don't have permission to ban members!", ephemeral=True)
            return

        await member.ban(reason=reason)
        await interaction.response.send_message(
            f"{member.display_name} has been banned. Reason: {reason or 'No reason provided'}"
        )
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to ban that member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="timeout", description="Timeouts a member")
@app_commands.describe(member="Member to timeout", duration="Duration in seconds (max 28 days)", reason="Reason for timeout")
@commands.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = None):
    try:
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You don't have permission to timeout members!", ephemeral=True)
            return

        if duration > 2419200:  # 28 days in seconds
            duration = 2419200
        
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=duration), reason=reason)
        await interaction.response.send_message(
            f"{member.display_name} has been timed out for {duration} seconds. Reason: {reason or 'No reason provided'}"
        )
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to timeout that member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="purge", description="Delete multiple messages at once")
@app_commands.describe(amount="Number of messages to delete (1-100)")
@commands.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    try:
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("You don't have permission to purge messages!", ephemeral=True)
            return

        if amount < 1 or amount > 100:
            await interaction.response.send_message("Amount must be between 1-100!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount + 1)
        await interaction.followup.send(
            f"Deleted {len(deleted)-1} messages", 
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to purge messages!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

bot.run(TOKEN)
