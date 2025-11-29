import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="quote", description="Get an inspirational quote")
    async def inspirational_quote(self, ctx):
        """Get random inspirational quote"""
        quotes = [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Innovation distinguishes between a leader and a follower. - Steve Jobs",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "Strive not to be a success, but rather to be of value. - Albert Einstein",
            "The way to get started is to quit talking and begin doing. - Walt Disney"
        ]
        
        embed = discord.Embed(
            title="💫 Inspirational Quote",
            description=random.choice(quotes),
            color=0xf39c12
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="poll", description="Create a quick poll")
    @app_commands.describe(question="The poll question", option1="First option", option2="Second option")
    async def create_poll(self, ctx, question: str, option1: str, option2: str):
        """Create a simple poll"""
        embed = discord.Embed(
            title="📊 Poll",
            description=question,
            color=0x9b59b6
        )
        embed.add_field(name="Option 1", value=option1, inline=True)
        embed.add_field(name="Option 2", value=option2, inline=True)
        embed.set_footer(text="React with 1️⃣ or 2️⃣ to vote!")
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")

async def setup(bot):
    await bot.add_cog(FunCommands(bot))async def setup(bot):
    await bot.add_cog(ModCommands(bot))
