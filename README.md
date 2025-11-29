# DigamberGPT V2 PRO — Discord AI Bot

A free, powerful AI chatbot for Discord using DeepSeek API.

## Features
- Responds only in the admin-set channel
- Slash Commands: `/setchannel #chat` and `/ask your_question`
- Typing indicator: "DigamberGPT is thinking..."
- Auto-delete links sent by users
- Message logs for each server
- Multi-server support
- Creator and identity locked to **DIGAMBER (thedigamber)**
- Premium role detection ready
- Works on all servers

## Setup

### 1. Clone Repo
```bash
git clone https://github.com/yourusername/digambergpt-v2-pro.git
```
cd digambergpt-v2-pro

2. Install Dependencies
```
pip install -r requirements.txt
```

3. Set Environment Variables (Render / local .env)
```
DISCORD_TOKEN=your_bot_token
DEEPSEEK_API_KEY=your_deepseek_key
```
4. Deploy to Render

Select Web Service → Python → Build Command auto → Start Command from Procfile

Logs auto-create & bot stays online.


5. Discord Setup

Set AI chat channel:


`/setchannel` #your-channel

Ask bot anything:


/ask What is the meaning of life?

Enjoy 🚀

---

# 6️⃣ **channels.json**  

```json
{}

> Auto-create first run pe.
