import os
import discord
import random
import asyncio
from gpt_utils import gpt_response
from keep_alive import keep_alive
from discord.ext import commands
from dotenv import load_dotenv

import wack

keep_alive()
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise RuntimeError('DISCORD_TOKEN is not set. Please add it to your .env file or environment variables.')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # needed for kick/ban/timeout targets

bot = commands.Bot(command_prefix='!', intents=intents)

MAX_DISCORD_MESSAGE_LENGTH = 2000


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

    is_registered_channel = wack.is_registered_channel(guild_id, channel_id)
    mention = bot.user.mentioned_in(message)
    should_random_reply = not is_registered_channel and random.random() < wack.RANDOM_CHAT_CHANCE

    image_urls = [attachment.url for attachment in message.attachments if not attachment.content_type or attachment.content_type.startswith('image')]

    if is_registered_channel or mention or should_random_reply:
        async with message.channel.typing():
            delay = random.uniform(1.5, 3.0)  # Random between 1.5 to 3 seconds
            await asyncio.sleep(delay)
            content = message.content
            if mention:
                content = message.content.replace(f'<@{bot.user.id}>', '').strip()
            conversation_id = f'{guild_id}-{channel_id}'
            reply = await gpt_response(
                content,
                wack.get_guild_language(guild_id),
                image_urls=image_urls,
                conversation_id=conversation_id,
                author_name=message.author.display_name
            )
            await send_long_message(message.channel, reply)

    await bot.process_commands(message)


async def main():
    async with bot:
        await bot.load_extension('commands')
        await bot.start(TOKEN)


asyncio.run(main())
