import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import timedelta

class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="setup", description="Setup AI channel for this server")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(channel="Channel where AI will respond")
    async def setup_ai_channel(self, ctx, channel: discord.TextChannel):
        """Setup AI channel for the server"""
        # In a real bot, you'd save this to a database
        embed = discord.Embed(
            title="✅ AI Channel Setup",
            description=f"AI features enabled in {channel.mention}",
            color=0x00ff00
        )
        embed.add_field(name="Available Commands", value="• /ai - Chat with AI\n• /image - Generate images\n• /clear - Clear chat history")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="purge", description="Delete multiple messages")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    async def purge_messages(self, ctx, amount: int = 10):
        """Bulk delete messages"""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Amount must be between 1-100", ephemeral=True)
            return
            
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"✅ Deleted {len(deleted) - 1} messages", delete_after=5)

async def setup(bot):
    await bot.add_cog(ModCommands(bot))
