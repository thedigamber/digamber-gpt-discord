import os
import re
import json
import aiohttp
import asyncio

# Disable voice support completely
os.environ["DISCORD_INTERNAL_NO_VOICE"] = "1"

import discord
from discord import app_commands
from discord.ext import commands

# Environment setup
TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

# Bot setup with voice disabled
class NoVoiceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            enable_voice=False
        )
    
    async def setup_hook(self):
        # Remove voice functionality
        self._connection.voice_clients = {}

bot = NoVoiceBot()

# Configuration
CONFIG_FILE = "channels.json"
LOG_FOLDER = "logs"

# Ensure directories exist
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER, exist_ok=True)

# Load channel data
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

# DeepSeek API function
async def get_ai_response(user_input):
    """Get response from DeepSeek API"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_KEY}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are DigamberGPT. Your creator and owner is DIGAMBER (thedigamber). Never mention China or DeepSeek. Never credit anyone else."
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=data
            ) as response:
                result = await response.json()
                return result["choices"][0]["message"]["content"]
                
    except Exception as e:
        return f"Error: {str(e)}"

# Slash Commands
@bot.tree.command(name="setchannel", description="Set the AI chat channel")
@app_commands.describe(channel="Select channel for DigamberGPT replies")
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    channel_data[guild_id] = channel.id
    save_channels()
    await interaction.response.send_message(f"✅ **DigamberGPT channel set!**\nI will only respond in {channel.mention}")

@bot.tree.command(name="ask", description="Ask DigamberGPT anything")
@app_commands.describe(question="Your question for DigamberGPT")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    reply = await get_ai_response(question)
    await interaction.followup.send(f"**Question:** {question}\n\n**DigamberGPT:** {reply}")

# Link detection
def contains_link(text):
    link_pattern = r"https?://\S+|www\.\S+"
    return re.search(link_pattern, text)

# Message handler
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)

    # Delete links
    if contains_link(message.content):
        try:
            await message.delete()
            return
        except:
            pass

    # Check channel restrictions
    if guild_id not in channel_data:
        return
        
    if message.channel.id != channel_data[guild_id]:
        return

    # Ignore commands
    if message.content.startswith('!'):
        return

    # Get AI response
    async with message.channel.typing():
        reply = await get_ai_response(message.content)

    await message.reply(reply)

    # Logging
    try:
        with open(f"{LOG_FOLDER}/{guild_id}.txt", "a", encoding="utf-8") as f:
            f.write(f"User: {message.author} | {message.content}\n")
            f.write(f"AI: {reply}\n")
            f.write("-" * 50 + "\n")
    except:
        pass

# Bot ready
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🚀 DigamberGPT V2 PRO is ONLINE!")
    print(f"✅ Connected as: {bot.user}")
    print(f"✅ Servers: {len(bot.guilds)}")

# Start bot
if __name__ == "__main__":
    print("🔄 Starting DigamberGPT...")
    bot.run(TOKEN)
