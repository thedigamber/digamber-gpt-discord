import discord
from discord.ext import commands, tasks
import os
import json
import asyncio
import aiohttp
from flask import Flask
from datetime import datetime
import traceback

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 DigamberGPT - Operational"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

TOKEN = os.getenv("DISCORD_TOKEN")

class ChatGPTBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.config = config
        self.start_time = datetime.now()
        self.session = None
        self.ai_channels = {}  # Store AI channels per server

    async def setup_hook(self):
        # Start session
        self.session = aiohttp.ClientSession()
        
        # Load cogs
        cogs = ['cogs.ai_commands', 'cogs.mod_commands']
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded: {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
                traceback.print_exc()
        
        # Sync commands with better handling
        try:
            print("🔄 Syncing slash commands...")
            synced = await self.tree.sync()
            print(f"✅ Successfully synced {len(synced)} slash commands")
            
            # Print all commands
            for cmd in synced:
                print(f"   - /{cmd.name}")
                
        except Exception as e:
            print(f"❌ Slash command sync failed: {e}")
            traceback.print_exc()
        
        # Start tasks
        self.update_presence.start()

    async def on_ready(self):
        print(f"\n🚀 {self.user} is ONLINE!")
        print(f"📊 Servers: {len(self.guilds)}")
        print(f"👥 Users: {sum(g.member_count for g in self.guilds)}")
        
        # Print available commands
        commands_list = [cmd.name for cmd in self.tree.get_commands()]
        print(f"🎯 Available commands: {', '.join(commands_list)}")
        
        # Start Flask in background for Render
        if os.environ.get('RENDER'):
            import threading
            threading.Thread(target=run_flask, daemon=True).start()
            print("🌐 Flask server started")

    async def on_guild_join(self, guild):
        """Auto-sync commands when bot joins new server"""
        try:
            await self.tree.sync(guild=guild)
            print(f"✅ Commands synced for new server: {guild.name}")
        except Exception as e:
            print(f"❌ Failed to sync commands for {guild.name}: {e}")

    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if message is in AI channel
        guild_id = str(message.guild.id)
        
        if guild_id in self.ai_channels:
            ai_channel_id = self.ai_channels[guild_id]
            
            # If message is in AI channel, process automatically
            if str(message.channel.id) == ai_channel_id:
                # Ignore commands
                if not message.content.startswith('!'):
                    await self.process_ai_message(message)
                    return
        
        # Process commands for other channels
        await self.process_commands(message)

    async def process_ai_message(self, message):
        """Process AI messages automatically"""
        try:
            # Get AI cog
            ai_cog = self.get_cog('AICommands')
            if ai_cog:
                async with message.channel.typing():
                    response = await ai_cog.get_ai_response(message.content)
                    
                    # Check if user wants image generation
                    if any(word in message.content.lower() for word in ['image', 'picture', 'photo', 'generate image', 'draw', 'create image']):
                        # Send image generation message
                        await message.reply("🖼️ Image generation feature coming soon! Currently I can only chat.")
                    else:
                        # Send AI response
                        await message.reply(response)
                        
        except Exception as e:
            print(f"AI processing error: {e}")

    @tasks.loop(minutes=10)
    async def update_presence(self):
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"),
            discord.Activity(type=discord.ActivityType.listening, name="ChatGPT-style AI"),
            discord.Activity(type=discord.ActivityType.playing, name="Auto-Response Mode")
        ]
        activity = activities[(datetime.now().minute // 10) % len(activities)]
        await self.change_presence(activity=activity)

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

# Run bot
if __name__ == "__main__":
    bot = DigamberGptBot()
    bot.run(TOKEN)
