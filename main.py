import os
import discord
import threading
import time
import json    
from gpt_utils import gpt_response
from keep_alive import keep_alive
keep_alive()
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

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

config = load_config()

def config_loop():
    while True:
        global config
        config = load_config()
        time.sleep(20)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='IamMepl'))
    await bot.tree.sync()
    print(f'{bot.user.name} online!')

@bot.event

async def on_message(message):
    if message.author == bot.user:
        return

    guild_id = str(message.guild.id)
    channel_id = str(message.channel.id)
    responded = False

    if guild_id in config and channel_id in config[guild_id]:
        await message.channel.send(gpt_response(message.content))
        responded = True

    if bot.user.mentioned_in(message) and not responded:
        await message.channel.send(gpt_response(message.content.replace(f'<@{bot.user.id}>', '').strip()))
        responded = True
        
    await bot.process_commands(message)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    
@bot.tree.command(name='unregister', description='Remove your channel id from database')
async def unregister(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    if guild_id in config and channel_id in config[guild_id]:
        config[guild_id].remove(channel_id)
        save_config(config)
        await interaction.response.send_message('This channel has been removed from the database.')


@bot.tree.command(name='register', description='register your channel id to database')
async def register(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    if guild_id not in config:
        config[guild_id] = []

    if channel_id not in config[guild_id]:
        config[guild_id].append(channel_id)
        save_config(config)
        await interaction.response.send_message('This channel has been registered from the database.')
        

bot.run(TOKEN)
