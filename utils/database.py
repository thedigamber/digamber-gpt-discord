import json
import aiofiles
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional

class JSONDatabase:
    def __init__(self, db_file: str = "data/database.json"):
        self.db_file = db_file
        self.ensure_directory()

    def ensure_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)

    async def read_data(self) -> Dict[str, Any]:
        """Read data from JSON file"""
        try:
            async with aiofiles.open(self.db_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content) if content else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    async def write_data(self, data: Dict[str, Any]):
        """Write data to JSON file"""
        async with aiofiles.open(self.db_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=4, ensure_ascii=False))

    async def get_guild_settings(self, guild_id: str) -> Dict[str, Any]:
        """Get guild-specific settings"""
        data = await self.read_data()
        return data.get('guilds', {}).get(guild_id, {})

    async def set_guild_settings(self, guild_id: str, settings: Dict[str, Any]):
        """Set guild-specific settings"""
        data = await self.read_data()
        if 'guilds' not in data:
            data['guilds'] = {}
        data['guilds'][guild_id] = settings
        await self.write_data(data)

    async def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user-specific data"""
        data = await self.read_data()
        return data.get('users', {}).get(user_id, {})

    async def set_user_data(self, user_id: str, user_data: Dict[str, Any]):
        """Set user-specific data"""
        data = await self.read_data()
        if 'users' not in data:
            data['users'] = {}
        data['users'][user_id] = user_data
        await self.write_data(data)

    async def increment_user_requests(self, user_id: str):
        """Increment user request count"""
        user_data = await self.get_user_data(user_id)
        user_data['total_requests'] = user_data.get('total_requests', 0) + 1
        user_data['last_used'] = datetime.now().isoformat()
        
        if 'first_used' not in user_data:
            user_data['first_used'] = datetime.now().isoformat()
            
        await self.set_user_data(user_id, user_data)

    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global bot statistics"""
        data = await self.read_data()
        return data.get('global_stats', {
            'total_requests': 0,
            'unique_users': 0,
            'guild_count': 0
        })

    async def update_global_stats(self, stats: Dict[str, Any]):
        """Update global bot statistics"""
        data = await self.read_data()
        data['global_stats'] = stats
        await self.write_data(data)

# Database instance
db = JSONDatabase()
