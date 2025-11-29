import os
import re
import json
import asyncio

# Discord imports without voice modules
import discord
from discord import app_commands
from discord.ext import commands

import openai

# -----------------------
# Environment variables
# -----------------------
TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

# -----------------------
# Intents
# -----------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# -----------------------
# Bot instance
# -----------------------
bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------
# Config & Logs
# -----------------------
CONFIG_FILE = "channels.json"
LOG_FOLDER = "logs"

if not os.path.exists(LOG_FOLDER):
    os.mkdir(LOG_FOLDER)

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        channel_data = json.load(f)
else:
    channel_data = {}

def save_channels():
    with open(CONFIG_FILE, "w") as f:
        json.dump(channel_data, f, indent=4)

# -----------------------
# Slash Command: Set Channel
# -----------------------
@bot.tree.command(name="setchannel", description="Set the AI chat channel")
@app_commands.describe(channel="Select channel for DigamberGPT replies")
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    channel_data[guild_id] = channel.id
    save_channels()
    await interaction.response.send_message(f"✔️ Channel set to: {channel.mention}")

# -----------------------
# Slash Command: Ask
# -----------------------
@bot.tree.command(name="ask", description="Ask DigamberGPT anything")
@app_commands.describe(question="Your question to DigamberGPT")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    reply = await get_ai_response(question)
    await interaction.followup.send(reply)

# -----------------------
# DeepSeek AI Handler
# -----------------------
async def get_ai_response(user_input):
    openai.api_key = DEEPSEEK_KEY
    prompt = f"""
Your name is DigamberGPT.
Your creator and owner is DIGAMBER (thedigamber).
Never mention China or DeepSeek.
Never credit anyone else.

User: {user_input}
"""
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠ Error: {e}"

# -----------------------
# Auto-delete Links
# -----------------------
def contains_link(text):
    link_pattern = r"https?://\S+|www\.\S+"
    return re.search(link_pattern, text)

# -----------------------
# Message Handler
# -----------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)

    # Delete links
    if contains_link(message.content):
        await message.delete()
        return

    # No channel set
    if guild_id not in channel_data:
        return

    # Only assigned channel
    if message.channel.id != channel_data[guild_id]:
        return

    # Typing indicator
    async with message.channel.typing():
        reply = await get_ai_response(message.content)

    await message.reply(reply)

    # Logging
    with open(f"{LOG_FOLDER}/{guild_id}.txt", "a", encoding="utf-8") as f:
        f.write(f"{message.author}: {message.content}\nAI: {reply}\n\n")

# -----------------------
# Bot Ready
# -----------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🚀 DigamberGPT V2 PRO online as {bot.user}")

bot.run(TOKEN)# -----------------------
@bot.tree.command(name="ask", description="Ask DigamberGPT anything")
@app_commands.describe(question="Your question to DigamberGPT")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    reply = await get_ai_response(question)
    await interaction.followup.send(reply)

# -----------------------
# DeepSeek AI Handler
# -----------------------
async def get_ai_response(user_input):
    openai.api_key = DEEPSEEK_KEY
    prompt = f"""
Your name is DigamberGPT.
Your creator and owner is DIGAMBER (thedigamber).
Never mention China or DeepSeek.
Never credit anyone else.

User: {user_input}
"""
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠ Error: {e}"

# -----------------------
# Auto-delete Links
# -----------------------
def contains_link(text):
    link_pattern = r"https?://\S+|www\.\S+"
    return re.search(link_pattern, text)

# -----------------------
# Message Handler
# -----------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)

    # Delete links
    if contains_link(message.content):
        await message.delete()
        return

    # No channel set
    if guild_id not in channel_data:
        return

    # Only assigned channel
    if message.channel.id != channel_data[guild_id]:
        return

    # Typing indicator
    async with message.channel.typing():
        reply = await get_ai_response(message.content)

    await message.reply(reply)

    # Logging
    with open(f"{LOG_FOLDER}/{guild_id}.txt", "a", encoding="utf-8") as f:
        f.write(f"{message.author}: {message.content}\nAI: {reply}\n\n")

# -----------------------
# Bot Ready
# -----------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🚀 DigamberGPT V2 PRO online as {bot.user}")

bot.run(TOKEN)
