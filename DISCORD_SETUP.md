# Discord Bot Setup Guide

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Node.js** installed (for RailKit SDK)
3. **Virtual environment** set up (`env5/`)
4. **All dependencies installed**:
   - Python: `pip install -r requirements.txt`
   - Node.js: `npm install`

## 🤖 Create Discord Bot

### Step 1: Create Application on Discord

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Give it a name (e.g., "Train Recommendation Bot")
4. Click **"Create"**

### Step 2: Create Bot User

1. In your application, go to the **"Bot"** tab
2. Click **"Add Bot"** → Confirm
3. Under **"Privileged Gateway Intents"**, enable:
   - ✅ **Message Content Intent** (optional - for future prefix commands)
   - ✅ **Server Members Intent** (optional)
   - ✅ **Presence Intent** (optional)
4. Click **"Reset Token"** and copy your bot token
5. **IMPORTANT**: Keep this token secret!

> **Note:** Slash commands don't require Message Content Intent, but enable it for future features.

### Step 3: Add Token to .env

Open `.env` file and replace:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

With your actual token:
```
DISCORD_TOKEN=YOUR_ACTUAL_BOT_TOKEN_HERE_REPLACE_THIS
```

### Step 4: Invite Bot to Your Server

1. In Discord Developer Portal, go to **"OAuth2"** → **"URL Generator"**
2. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands` (REQUIRED for slash commands!)
3. Select bot permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
4. Copy the generated URL
5. Open URL in browser and select your server
6. Click **"Authorize"**

> **Important:** Make sure to select `applications.commands` scope for slash commands to work!

## 🚀 Running the Bot

### Start MCP Server (Terminal 1)

```powershell
# Activate virtual environment
.\env5\Scripts\Activate.ps1

# Run MCP server
.\env5\Scripts\python.exe run_server.py
```

You should see:
```
🔧 FastMCP server starting...
✅ Server ready with 3 tools
```

### Start Discord Bot (Terminal 2)

```powershell
# Activate virtual environment
.\env5\Scripts\Activate.ps1

# Run Discord bot
.\env5\Scripts\python.exe run_bot.py
```

You should see:
```
🚀 Starting Discord bot...
📋 Slash Commands:
  /train <query>  - Search for trains
  /ping           - Check bot latency
🤖 TrainBot#1234 is now online!
📊 Connected to 1 server(s)
```

> **Note:** The bot uses **slash commands** now, not prefix commands (no more `!train`)!

## 💬 Using the Bot

### Slash Commands

The bot uses **modern Discord slash commands**. Just type `/` in any channel to see available commands!

#### `/train <query>`
Get train recommendations based on natural language query

**Examples:**
```
/train I want to travel from Mumbai to Delhi tomorrow with budget 5000

/train Find trains from Chennai to Bangalore on 2026-08-20, AC 3 Tier, morning departure

/train Book me a sleeper class train from Kolkata to Mumbai next week, budget 3000

/train Delhi to Mumbai on August 15th, AC 2 Tier, morning departure
```

#### `/ping`
Check bot latency and response time

**How to use slash commands:**
1. Type `/` in Discord chat
2. Click on the bot's command from the menu
3. Fill in the required parameters
4. Press Enter

## 🎨 Bot Features

✅ **Modern slash commands** (no more prefix commands!)
✅ **Natural language understanding** (powered by GPT-4o/Claude)
✅ **Station name resolution** (handles "Mumbai" → station codes automatically)
✅ **Multi-API integration**:
   - RailRadar API (station & train search)
   - RailKit API (seat availability & fares)
✅ **Smart filtering**:
   - Budget filtering
   - Class preference filtering  
   - Time preference filtering
   - Date parsing (understands "tomorrow", "next week", etc.)
✅ **Beautiful Discord embeds** with train details
✅ **Error handling** with helpful messages
✅ **Real-time seat availability** from RailKit
✅ **Optimized API usage** (checks only top 3 trains for availability)
✅ **Workflow orchestration** using LangGraph

## 🛠️ Troubleshooting

### Slash commands don't appear
- ✅ Check bot was invited with `applications.commands` scope
- ✅ Wait 5-10 minutes for Discord to sync commands
- ✅ Try kicking and re-inviting the bot
- ✅ Check bot has proper permissions in the server

### Bot doesn't respond to slash commands
- ✅ Verify bot is online (green status in server)
- ✅ Check **MCP server is running** in Terminal 1
- ✅ Verify bot has "Send Messages" permission in the channel
- ✅ Look for error messages in bot console

### "DISCORD_TOKEN not found" error
- ✅ Check `.env` file exists in project root
- ✅ Verify `.env` has `DISCORD_TOKEN=your_token`
- ✅ No spaces around `=`
- ✅ Token is on the same line

### "No trains found" every time
- ✅ **MCP server must be running first** (`run_server.py`)
- ✅ API keys in `.env` are valid:
  - `RAILRADAR_API_KEY`
  - `RAILKIT_API_KEY`
- ✅ Try different station names or dates
- ✅ Check console for API error messages

### "Cannot find module 'railkit'" error
- ✅ Install Node.js dependencies: `npm install`
- ✅ Check `node_modules/railkit/` exists
- ✅ Verify Node.js is installed: `node --version`

### Import errors / Module not found
- ✅ Virtual environment is activated
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Use the correct entry points: `run_server.py` and `run_bot.py`

### Bot connects but workflow fails
- ✅ Check MCP server is running FIRST
- ✅ Look for initialization messages: "🔧 Initializing MCP client..."
- ✅ Verify all 3 tools loaded successfully
- ✅ Check Terminal 1 for MCP server errors

## 📂 File Structure

```
train_mcp_server/
├── src/
│   ├── api/
│   │   ├── train_api.py           # Train API integrations (RailRadar, RailKit)
│   │   └── railkit_wrapper.js     # Node.js wrapper for RailKit SDK
│   ├── server/
│   │   ├── server.py              # MCP server (FastMCP)
│   │   └── tools.py               # MCP tools & client initialization
│   ├── workflow/
│   │   └── orchestration.py      # LangGraph workflow
│   ├── bot/
│   │   └── discord_bot.py         # Discord bot (slash commands)
│   └── config/
│       └── config.py              # Configuration & API keys
├── tests/                         # Test files
│   ├── test_*.py
│   └── manual_test.py
├── node_modules/                  # Node.js packages (RailKit SDK)
├── env5/                          # Python virtual environment
├── run_server.py                  # Entry point: MCP server
├── run_bot.py                     # Entry point: Discord bot
├── .env                           # Environment variables (SECRET!)
├── requirements.txt               # Python dependencies
├── package.json                   # Node.js dependencies
├── README.md                      # Project documentation
└── DISCORD_SETUP.md              # This file!
```

## 🔒 Security Notes

⚠️ **NEVER share or commit your .env file!**
⚠️ Keep your Discord token secret
⚠️ Add `.env` to `.gitignore`

## 🎯 Next Steps

1. ✅ Test the bot with various queries
2. ✅ Customize embed colors and messages in `src/bot/discord_bot.py`
3. 🔲 Add more slash commands (e.g., `/status`, `/help`, `/about`)
4. 🔲 Implement conversation context for follow-up questions
5. 🔲 Add PNR status checking command
6. 🔲 Add fare comparison across multiple trains
7. 🔲 Implement train tracking (live running status)
8. 🔲 Add user preferences (save favorite routes, classes)

## 📝 Example Usage

User types in Discord:
```
/train query: I want to go from Mumbai to Delhi on August 20th, 2026. My budget is 5000 rupees and I prefer AC 3 Tier class with morning departure.
```

Bot Response (Beautiful Embed):
```
🚂 Train Recommendations

━━━━━━━━━━━━━━━━━━━━━━━━━━
🚂 12951 - Mumbai Central Rajdhani
━━━━━━━━━━━━━━━━━━━━━━━━━━

🏙️ Route
   Mumbai Central (MMCT) → New Delhi (NDLS)

📅 Schedule
   🕐 Departure: 06:30 AM
   🕐 Arrival: 08:35 PM
   ⏱️ Duration: 14h 5m

💰 Pricing
   ₹4,850 - AC 3-Tier (3A)
   
🎫 Availability
   ✅ Available - 25 seats

📝 Why this train?
   Fastest direct train with excellent on-time 
   performance. Perfect for morning departure.
━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Powered by Train Recommendation System
```

**More Examples:**

Simple query:
```
/train query: Delhi to Mumbai tomorrow
```

Detailed query:
```
/train query: Chennai to Bangalore on 15th August, sleeper class, budget 1500
```

Natural language:
```
/train query: Find me a cheap train from Kolkata to Goa next week
```

## 🔑 Required Environment Variables

Make sure your `.env` file has all these:

```env
# Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# RailRadar API Key (for station & train search)
RAILRADAR_API_KEY=your_railradar_api_key

# RailKit API Key (for seat availability)
RAILKIT_API_KEY=your_railkit_api_key

# Optional: IRCTC2 API Key (not currently used, but reserved)
IRCTC2_API_KEY=your_irctc2_api_key
```

## 📊 How It Works

```
User types slash command in Discord
          ↓
Discord Bot (run_bot.py)
          ↓
LangGraph Workflow (orchestration.py)
          ↓
MCP Tools (tools.py) ← Connects to MCP Server
          ↓
MCP Server (run_server.py)
          ↓
Train APIs (train_api.py)
          ↓
External APIs:
  ├─ RailRadar (station search, train search)
  └─ RailKit (seat availability, fares)
          ↓
Results flow back to Discord
```

## ⚡ Performance Optimizations

- ✅ **Lazy loading:** MCP client initializes on first use
- ✅ **Tool caching:** Tools loaded once and reused
- ✅ **API optimization:** Only checks top 3 trains for availability (saves 60-70% API calls)
- ✅ **Async operations:** Non-blocking workflow execution
- ✅ **Connection pooling:** Reuses MCP server connection

## 🆘 Support

If you encounter issues:
1. Check **both terminal outputs** for error messages
2. Verify **all environment variables** are set in `.env`
3. Ensure **MCP server runs FIRST** before starting bot
4. Test APIs directly with test scripts in `tests/` folder
5. Check Node.js dependencies: `npm list railkit`
6. Verify Python imports: `python -c "from src.api import train_api"`

## 📚 Additional Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

Happy training! 🚂✨

**Need help?** Check the main `README.md` for more details!
