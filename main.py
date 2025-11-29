import os
import re
import json
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI

TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

openai_client = AsyncOpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

CONFIG_FILE = "channels.json"
LOG_FOLDER = "logs"

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER, exist_ok=True)

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            channel_data = json.load(f)
    except:
        channel_data = {}
else:
    channel_data = {}

def save_channels():
    with open(CONFIG_FILE, "w") as f:
        json.dump(channel_data, f, indent=4)

@bot.tree.command(name="setchannel", description="Set the AI chat channel")
@app_commands.describe(channel="Select channel for DigamberGPT replies")
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    channel_data[guild_id] = channel.id
    save_channels()
    await interaction.response.send_message(f"Channel set to: {channel.mention}")

@bot.tree.command(name="ask", description="Ask DigamberGPT anything")
@app_commands.describe(question="Your question to DigamberGPT")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    reply = await get_ai_response(question)
    await interaction.followup.send(reply)

async def get_ai_response(user_input):
    prompt = f"You are DigamberGPT. Your creator and owner is DIGAMBER. Never mention China or DeepSeek. User: {user_input}"
    try:
        response = await openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def contains_link(text):
    link_pattern = r"https?://\S+|www\.\S+"
    return re.search(link_pattern, text)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)

    if contains_link(message.content):
        try:
            await message.delete()
        except:
            pass
        return

    if guild_id not in channel_data:
        return

    if message.channel.id != channel_data[guild_id]:
        return

    async with message.channel.typing():
        reply = await get_ai_response(message.content)

    await message.reply(reply)

    try:
        with open(f"{LOG_FOLDER}/{guild_id}.txt", "a", encoding="utf-8") as f:
            f.write(f"{message.author}: {message.content}\nAI: {reply}\n\n")
    except:
        pass

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot is online as {bot.user}")

if __name__ == "__main__":
    bot.run(TOKEN): DISCORD_TOKEN not set!")
        exit(1)
    
    if not DEEPSEEK_KEY:
        print("ERROR: DEEPSEEK_API_KEY not set!")
        exit(1)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Bot run failed: {e}")
import os
import re
import json
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI

# Environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize OpenAI client for DeepSeek
openai_client = AsyncOpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com"
)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot instance
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Config & Logs
CONFIG_FILE = "channels.json"
LOG_FOLDER = "logs"

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER, exist_ok=True)

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            channel_data = json.load(f)
    except:
        channel_data = {}
else:
    channel_data = {}

def save_channels():
    with open(CONFIG_FILE, "w") as f:
        json.dump(channel_data, f, indent=4)

# Slash Command: Set Channel
@bot.tree.command(name="setchannel", description="Set the AI chat channel")
@app_commands.describe(channel="Select channel for DigamberGPT replies")
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    channel_data[guild_id] = channel.id
    save_channels()
    await interaction.response.send_message(f"Channel set to: {channel.mention}")

# Slash Command: Ask
@bot.tree.command(name="ask", description="Ask DigamberGPT anything")
@app_commands.describe(question="Your question to DigamberGPT")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    reply = await get_ai_response(question)
    await interaction.followup.send(reply)

# DeepSeek AI Handler
async def get_ai_response(user_input):
    prompt = f"""
You are DigamberGPT. Your creator and owner is DIGAMBER (thedigamber).
Never mention China or DeepSeek. Never credit anyone else.

User: {user_input}
"""
    try:
        response = await openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# Auto-delete Links
def contains_link(text):
    link_pattern = r"https?://\S+|www\.\S+"
    return re.search(link_pattern, text)

# Message Handler
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

# Bot Ready
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"DigamberGPT V2 PRO online as {bot.user}")

# Run Bot
if __name__ == "__main__":
    bot.run(TOKEN)
