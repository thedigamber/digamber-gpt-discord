import discord
import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import random

class Helpers:
    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds into human readable time"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"

    @staticmethod
    def create_embed(
        title: str,
        description: str = "",
        color: int = 0x3498db,
        fields: List[Dict[str, Any]] = None,
        thumbnail: str = None,
        footer: str = None,
        author: str = None
    ) -> discord.Embed:
        """Create a formatted embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', '\u200b'),
                    value=field.get('value', '\u200b'),
                    inline=field.get('inline', False)
                )
                
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
            
        if footer:
            embed.set_footer(text=footer)
            
        if author:
            embed.set_author(name=author)
            
        return embed

    @staticmethod
    def contains_links(text: str) -> bool:
        """Check if text contains URLs"""
        url_pattern = r'https?://\S+|www\.\S+'
        return bool(re.search(url_pattern, text, re.IGNORECASE))

    @staticmethod
    def clean_content(text: str, max_length: int = 2000) -> str:
        """Clean and truncate text content"""
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
            
        return text

    @staticmethod
    def get_random_color() -> int:
        """Get a random discord color"""
        colors = [
            0x1abc9c, 0x2ecc71, 0x3498db, 0x9b59b6, 
            0xe91e63, 0xf1c40f, 0xe67e22, 0xe74c3c
        ]
        return random.choice(colors)

    @staticmethod
    def is_admin(ctx) -> bool:
        """Check if user has admin permissions"""
        return ctx.author.guild_permissions.administrator

    @staticmethod
    def format_number(number: int) -> str:
        """Format large numbers with K/M suffix"""
        if number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return str(number)

    @staticmethod
    def calculate_uptime(start_time: datetime) -> str:
        """Calculate uptime from start time"""
        uptime = datetime.now() - start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

# Helper instance
helpers = Helpers()
