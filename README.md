```markdown
# 🤖 DigamberGPT - AI Discord Bot

A powerful AI chatbot for Discord using DeepSeek API.

## 🚀 Features

- ✅ AI-powered responses using DeepSeek
- ✅ Channel-specific responses
- ✅ Auto-delete links
- ✅ Slash commands (/setchannel, /ask)
- ✅ Multi-server support
- ✅ Creator: DIGAMBER (thedigamber)

## Requirements

- Python 3.8+
- Discord bot token
- DeepSeek API key

## Installation

1. Clone repository:
```sh
git clone https://github.com/thedigamber/digamber-gpt-bot
cd digamber-gpt-bot
```

1. Install dependencies:

```sh
pip install -r requirements.txt
```

1. Create .env file:

```ini
DISCORD_TOKEN=your_bot_token
DEEPSEEK_API_KEY=your_deepseek_key
```

1. Run the bot:

```sh
python app.py
```

📚 Bot Commands

/setchannel #channel

Set the AI chat channel for DigamberGPT

/ask [question]

Ask DigamberGPT anything

🔧 Setup

1. Create Discord bot in Developer Portal
2. Set environment variables
3. Deploy to Render/Railway

Technologies Used

· Python
· Discord.py
· DeepSeek API
· Flask

License

MIT License

Author

DIGAMBER (thedigamber)

```

---

### 📄 **5. requirements.txt** (UPDATED)
```txt
discord.py>=2.3.2
python-dotenv>=1.0.0
Flask>=2.3.2
aiohttp>=3.8.4
openai>=1.6.1
```
