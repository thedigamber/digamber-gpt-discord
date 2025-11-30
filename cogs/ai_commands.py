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
        self.cooldowns = }

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
        # Universal approach for both slash and text commands
        try:
            # Defer only for slash commands
            if ctx.interaction:
                await ctx.defer()
            
            reply = await self.get_ai_response(question)
            
            # Send response based on command type
            if ctx.interaction:
                await ctx.followup.send(f"**{ctx.author.display_name}:** {question}\n\n**DigamberGPT:** {reply}")
            else:
                await ctx.send(f"**{ctx.author.display_name}:** {question}\n\n**DigamberGPT:** {reply}")
                
        except Exception as e:
            error_msg = f"❌ Command error: {str(e)}"
            if ctx.interaction:
                await ctx.followup.send(error_msg)
            else:
                await ctx.send(error_msg)

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
        try:
            if ctx.interaction:
                await ctx.defer()
            
            response = await self.get_ai_response("Hello, who are you?")
            
            if "❌" in response or "⚠️" in response:
                if ctx.interaction:
                    await ctx.followup.send(f"❌ **Test Failed:** {response}")
                else:
                    await ctx.send(f"❌ **Test Failed:** {response}")
            else:
                if ctx.interaction:
                    await ctx.followup.send(f"✅ **Test Successful!**\n\n**AI Response:** {response}")
                else:
                    await ctx.send(f"✅ **Test Successful!**\n\n**AI Response:** {response}")
                    
        except Exception as e:
            error_msg = f"❌ Test error: {str(e)}"
            if ctx.interaction:
                await ctx.followup.send(error_msg)
            else:
                await ctx.send(error_msg)

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
