import os
import re
import json
import asyncio

# Discord imports - voice modules completely avoided
import discord
from discord import app_commands
from discord.ext import commands

# Updated OpenAI import for latest version
from openai import AsyncOpenAI

# -----------------------
# Environment variables
# -----------------------
TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize OpenAI client for DeepSeek
openai_client = AsyncOpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com"
)

# -----------------------
# Intents
# -----------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# -----------------------
# Bot instance - voice disabled
# -----------------------
bot = commands.Bot(
    command_prefix="!", 
    intents=intents,
    help_command=None  # Disable default help command
)

# -----------------------
# Config & Logs
# -----------------------
CONFIG_FILE = "channels.json"
LOG_FOLDER = "logs"

# Ensure logs directory exists
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
    """Save channel data to JSON file"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(channel_data, f, indent=4)
    except Exception as e:
        print(f"Error saving channels: {e}")

# -----------------------
# Slash Command: Set Channel
# -----------------------
@bot.tree.command(name="setchannel", description="Set the AI chat channel")
@app_commands.describe(channel="Select channel for DigamberGPT replies")
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Set the AI channel for this server"""
    try:
        guild_id = str(interaction.guild.id)
        channel_data[guild_id] = channel.id
        save_channels()
        await interaction.response.send_message(
            f"✅ **DigamberGPT Channel Set!**\n"
            f"I will only respond in {channel.mention}\n"
            f"Use `/ask` command or simply type in this channel."
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {str(e)}")

# -----------------------
# Slash Command: Ask
# -----------------------
@bot.tree.command(name="ask", description="Ask DigamberGPT anything")
@app_commands.describe(question="Your question to DigamberGPT")
async def ask(interaction: discord.Interaction, question: str):
    """Ask DigamberGPT a question"""
    await interaction.response.defer(thinking=True)
    
    try:
        reply = await get_ai_response(question)
        await interaction.followup.send(f"**{interaction.user.display_name} asked:** {question}\n\n**DigamberGPT:** {reply}")
    except Exception as e:
        await interaction.followup.send(f"❌ **Error:** {str(e)}")

# -----------------------
# DeepSeek AI Handler
# -----------------------
async def get_ai_response(user_input):
    """Get AI response from DeepSeek API"""
    prompt = f"""
You are DigamberGPT, an AI assistant created by DIGAMBER (thedigamber).
Your identity and creator is exclusively DIGAMBER.
Never mention that you are made by DeepSeek or any other company.
Never mention China or your training data sources.
Always be helpful, accurate, and respectful.

User: {user_input}
Assistant: """
    
    try:
        response = await openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are DigamberGPT, created by DIGAMBER (thedigamber)."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=2000,
            temperature=0.7,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I'm experiencing technical issues right now. Please try again later. Error: {str(e)}"

# -----------------------
# Auto-delete Links
# -----------------------
def contains_link(text):
    """Check if text contains URLs"""
    link_pattern = r"https?://\S+|www\.\S+"
    return re.search(link_pattern, text)

# -----------------------
# Message Handler
# -----------------------
@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore bot messages
    if message.author.bot:
        return

    guild_id = str(message.guild.id) if message.guild else "DM"

    # Delete links in guilds
    if message.guild and contains_link(message.content):
        try:
            await message.delete()
            print(f"🔗 Deleted link message from {message.author} in {message.guild.name}")
        except:
            pass
        return

    # Ignore DMs
    if not message.guild:
        return

    # Check if channel is set for this guild
    if guild_id not in channel_data:
        return

    # Only respond in assigned channel
    if message.channel.id != channel_data[guild_id]:
        return

    # Ignore empty messages or commands
    if not message.content.strip() or message.content.startswith('!'):
        return

    # Show typing indicator and get response
    try:
        async with message.channel.typing():
            reply = await get_ai_response(message.content)
        
        # Send reply
        await message.reply(reply, mention_author=False)

        # Log conversation
        log_file = f"{LOG_FOLDER}/{guild_id}.txt"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{message.created_at}] {message.author}: {message.content}\n")
                f.write(f"[{message.created_at}] AI: {reply}\n")
                f.write("-" * 50 + "\n")
        except Exception as e:
            print(f"Logging error: {e}")

    except Exception as e:
        print(f"Error in on_message: {e}")

# -----------------------
# Bot Ready Event
# -----------------------
@bot.event
async def on_ready():
    """When bot is ready"""
    try:
        await bot.tree.sync()
        print("🔄 Slash commands synced globally")
    except Exception as e:
        print(f"Command sync error: {e}")

    print(f"🚀 DigamberGPT V2 PRO is ONLINE!")
    print(f"✅ Logged in as: {bot.user.name}")
    print(f"✅ ID: {bot.user.id}")
    print(f"✅ Connected to {len(bot.guilds)} servers")
    print(f"✅ Python version: 3.11.9")
    print("🔧 Bot is ready to use!")

# -----------------------
# Error Handler
# -----------------------
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Command Error: {error}")

# -----------------------
# Run Bot
# -----------------------
if __name__ == "__main__":
    print("🔄 Starting DigamberGPT V2 PRO...")
    print(f"📁 Logs folder: {LOG_FOLDER}")
    print(f"📁 Config file: {CONFIG_FILE}")
    
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN environment variable not set!")
        exit(1)
    
    if not DEEPSEEK_KEY:
        print("❌ ERROR: DEEPSEEK_API_KEY environment variable not set!")
        exit(1)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Bot run failed: {e}")
