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
    return "🤖 Advance AI Bot - Operational"

@app.route('/status')
def status():
    return {"status": "online", "timestamp": datetime.now().isoformat()}

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

class AdvanceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=config['settings']['prefix'],
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.config = config
        self.start_time = datetime.now()
        self.session = None

    async def setup_hook(self):
        # Start session
        self.session = aiohttp.ClientSession()
        
        # Load cogs
        cogs = [
            'cogs.ai_commands',
            'cogs.mod_commands', 
            'cogs.fun_commands'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded: {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
                traceback.print_exc()
        
        # Sync commands
        await self.tree.sync()
        print("✅ Slash commands synced")
        
        # Start tasks
        self.update_presence.start()
        self.cleanup_temp.start()

    async def on_ready(self):
        print(f"\n🚀 {self.user} is ONLINE!")
        print(f"📊 Servers: {len(self.guilds)}")
        print(f"👥 Users: {sum(g.member_count for g in self.guilds)}")
        print(f"⏰ Started: {self.start_time}")
        
        # Start Flask in background for Render
        if os.environ.get('RENDER'):
            import threading
            threading.Thread(target=run_flask, daemon=True).start()
            print("🌐 Flask server started")

    async def on_message(self, message):
        if message.author.bot:
            return
            
        # Auto-moderation
        await self.auto_moderate(message)
        await self.process_commands(message)

    async def auto_moderate(self, message):
        """Auto moderation features"""
        content = message.content.lower()
        
        # Delete links if enabled
        if self.config['settings']['delete_links']:
            if any(link in content for link in ['http://', 'https://', 'www.']):
                try:
                    await message.delete()
                    await message.channel.send(
                        f"❌ {message.author.mention}, Links are not allowed here!",
                        delete_after=5
                    )
                    return
                except:
                    pass

    @tasks.loop(minutes=10)
    async def update_presence(self):
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"),
            discord.Activity(type=discord.ActivityType.listening, name="/ai | DigamberGPT"),
            discord.Activity(type=discord.ActivityType.playing, name="Advanced AI Mode")
        ]
        activity = activities[(datetime.now().minute // 10) % len(activities)]
        await self.change_presence(activity=activity)

    @tasks.loop(hours=24)
    async def cleanup_temp(self):
        """Daily cleanup tasks"""
        print("🧹 Performing daily cleanup...")

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

# Run bot
if __name__ == "__main__":
    bot = AdvanceBot()
    bot.run(os.getenv("DISCORD_TOKEN"))
