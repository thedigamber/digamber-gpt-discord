import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import json
import os
import re
from openai import AsyncOpenAI

CONFIG_FILE = "channels.json"

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.config_data = self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {"servers": {}}
        return {"servers": {}}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config_data, f, indent=4)

    async def is_channel_allowed(self, ctx):
        guild_id = str(ctx.guild.id)
        allowed = self.config_data["servers"].get(guild_id, {}).get("ai_channels", [])
        return True if not allowed else str(ctx.channel.id) in allowed

    @commands.hybrid_command(name="setchannel", description="Set the AI chat channel")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        self.config_data["servers"].setdefault(guild_id, {"ai_channels": []})
        
        if str(channel.id) not in self.config_data["servers"][guild_id]["ai_channels"]:
            self.config_data["servers"][guild_id]["ai_channels"].append(str(channel.id))
            self.save_config()

        await ctx.reply(f"✅ DigamberGPT channel set to: {channel.mention}")

    @commands.hybrid_command(name="ask", description="Ask DigamberGPT anything")
    @app_commands.describe(question="Your question to DigamberGPT")
    async def ask_ai(self, ctx, question: str):
        await ctx.defer()
        reply = await self.get_ai_response(question)
        await ctx.followup.send(f"**Question:** {question}\n\n**DigamberGPT:** {reply}")

    async def get_ai_response(self, user_input):
        prompt = f"""
You are DigamberGPT. Your creator and owner is DIGAMBER (thedigamber).
Never mention China or DeepSeek. Never credit anyone else.

User: {user_input}
"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def contains_link(self, text):
        link_pattern = r"https?://\S+|www\.\S+"
        return re.search(link_pattern, text)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)

        if self.contains_link(message.content):
            try:
                await message.delete()
                return
            except:
                pass

        if guild_id not in self.config_data["servers"]:
            return
            
        if str(message.channel.id) not in self.config_data["servers"][guild_id]["ai_channels"]:
            return

        if message.content.startswith('!'):
            return

        async with message.channel.typing():
            reply = await self.get_ai_response(message.content)

        await message.reply(reply)

async def setup(bot):
    await bot.add_cog(AICommands(bot))
