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
            prompt = f"""
You are DigamberGPT, an advanced AI assistant created by DIGAMBER. 
You are helpful, creative, and intelligent. 
Never mention that you are an AI model or your training data.
Respond naturally and helpfully.

User: {user_input}
"""
            
            response = self.groq.chat.completions.create(
                model="llama-3.1-8b-instant",  # 🚨 UPDATED MODEL
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Error: {str(e)}"

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

    def update_stats(self, user_id):
        """Update user statistics"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {"requests": 0, "first_use": datetime.now()}
        self.user_stats[user_id]["requests"] += 1

async def setup(bot):
    await bot.add_cog(AICommands(bot))
