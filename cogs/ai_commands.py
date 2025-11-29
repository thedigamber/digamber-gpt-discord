import discord
from discord.ext import commands
from discord import app_commands
import json
import aiohttp
import asyncio
from groq import Groq
from datetime import datetime, timedelta
import aiofiles

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.conversations = {}
        self.user_stats = {}
        self.cooldowns = {}

    @commands.hybrid_command(name="ai", description="Chat with advanced AI")
    @app_commands.describe(message="Your message to the AI", context="Additional context (optional)")
    async def ai_chat(self, ctx, message: str, context: str = None):
        """Advanced AI chat with context memory"""
        # Cooldown check
        if await self.check_cooldown(ctx):
            return
            
        await ctx.defer()
        
        # Get or create conversation
        conv_id = f"{ctx.guild.id}-{ctx.channel.id}"
        if conv_id not in self.conversations:
            self.conversations[conv_id] = []
            
        # Build conversation context
        messages = self.conversations[conv_id][-10:]  # Keep last 10 messages
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.groq.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=0.8,
                max_tokens=1500
            )
            
            reply = response.choices[0].message.content
            
            # Update conversation
            messages.append({"role": "assistant", "content": reply})
            self.conversations[conv_id] = messages
            
            # Update stats
            self.update_stats(ctx.author.id)
            
            # Send response
            embed = discord.Embed(
                title="🤖 DigamberGPT Response",
                description=reply,
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Error: {str(e)}")

    @commands.hybrid_command(name="image", description="Generate AI images")
    @app_commands.describe(prompt="Description of the image you want")
    async def generate_image(self, ctx, prompt: str):
        """AI image generation (placeholder - can integrate with stable diffusion)"""
        await ctx.defer()
        
        # This is a placeholder - you can integrate with actual image generation APIs
        embed = discord.Embed(
            title="🎨 Image Generation",
            description=f"**Prompt:** {prompt}\n\n*Image generation feature coming soon!*",
            color=0x9b59b6
        )
        await ctx.followup.send(embed=embed)

    @commands.hybrid_command(name="clear", description="Clear conversation history")
    async def clear_chat(self, ctx):
        """Clear AI conversation history"""
        conv_id = f"{ctx.guild.id}-{ctx.channel.id}"
        if conv_id in self.conversations:
            self.conversations[conv_id] = []
            await ctx.send("✅ Conversation history cleared!")
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

    async def check_cooldown(self, ctx):
        """Check and enforce cooldown"""
        user_id = ctx.author.id
        now = datetime.now()
        
        if user_id in self.cooldowns:
            last_used = self.cooldowns[user_id]
            if now - last_used < timedelta(seconds=5):
                await ctx.send("⏳ Please wait 5 seconds between commands!", ephemeral=True)
                return True
                
        self.cooldowns[user_id] = now
        return False

    def update_stats(self, user_id):
        """Update user statistics"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {"requests": 0, "first_use": datetime.now()}
        self.user_stats[user_id]["requests"] += 1

async def setup(bot):
    await bot.add_cog(AICommands(bot))
