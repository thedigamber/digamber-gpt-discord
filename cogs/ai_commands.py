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
    bot = ChatGPTBot()
    bot.run(TOKEN)

ye le app.py ki code and 👇 ye le

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from groq import Groq
from datetime import datetime, timedelta

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.conversations = {}
        self.user_stats = {}
        self.cooldowns = {}

    async def get_ai_response(self, user_input):
        """Get AI response - used by both commands and auto-response"""
        try:
            # Check if API key is set
            if not os.getenv("GROQ_API_KEY"):
                return "❌ **Configuration Error:** Groq API key not set. Please check environment variables."
            
            prompt = f"""
You are DigamberGPT, an advanced AI assistant created by DIGAMBER. 
You are helpful, creative, and intelligent. 
Never mention that you are an AI model or your training data.
Respond naturally and helpfully.

User: {user_input}
"""
            
            response = self.groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower():
                return "❌ **API Error:** Invalid Groq API key. Please check your environment variables."
            elif "rate limit" in error_msg.lower():
                return "⚠️ **Rate Limit:** Too many requests. Please try again in a moment."
            else:
                return f"❌ **Error:** {error_msg}"

    @commands.hybrid_command(name="ask", description="Ask anything to AI")
    @app_commands.describe(question="Your question")
    async def ask_ai(self, ctx, question: str):
        """AI command for non-AI channels"""
        await ctx.defer()
        
        reply = await self.get_ai_response(question)
        await ctx.followup.send(f"**{ctx.author.display_name}:** {question}\n\n**DigamberGPT:** {reply}")

    @commands.hybrid_command(name="clear", description="Clear your conversation history")
    async def clear_chat(self, ctx):
        """Clear AI conversation history"""
        user_id = ctx.author.id
        if user_id in self.conversations:
            self.conversations[user_id] = []
            await ctx.send("✅ Your conversation history cleared!")
        else:
            await ctx.send("ℹ️ No conversation history to clear.")

    @commands.hybrid_command(name="stats", description="Check your AI usage stats")
    async def user_stats(self, ctx):
        """Show user statistics"""
        user_id = ctx.author.id
        stats = self.user_stats.get(user_id, {"requests": 0, "first_use": datetime.now()})
        
        embed = discord.Embed(
            title="📊 Your AI Stats",
            color=0x3498db,
            timestamp=datetime.now()
        )
        embed.add_field(name="Total Requests", value=stats["requests"], inline=True)
        embed.add_field(name="First Use", value=stats["first_use"].strftime("%Y-%m-%d"), inline=True)
        embed.set_footer(text="Keep exploring! 🚀")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ping", description="Check bot status")
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! **Latency:** {latency}ms\n**Status:** Online ✅")

    @commands.hybrid_command(name="test", description="Test AI functionality")
    async def test_ai(self, ctx):
        """Test AI with simple question"""
        await ctx.defer()
        response = await self.get_ai_response("Hello, who are you?")
        
        if "❌" in response or "⚠️" in response:
            await ctx.followup.send(f"❌ **Test Failed:** {response}")
        else:
            await ctx.followup.send(f"✅ **Test Successful!**\n\n**AI Response:** {response}")

    @commands.hybrid_command(name="setchannel", description="Set AI auto-response channel")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Set AI channel for auto-response"""
        try:
            self.bot.ai_channels[str(ctx.guild.id)] = str(channel.id)
            await ctx.send(f"✅ **AI Channel Set!**\nI will auto-respond in {channel.mention}")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    def update_stats(self, user_id):
        """Update user statistics"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {"requests": 0, "first_use": datetime.now()}
        self.user_stats[user_id]["requests"] += 1

async def setup(bot):
    await bot.add_cog(AICommands(bot))
