# 🚂 Train Recommendation Discord Bot

A Discord bot that recommends trains using LangGraph workflow, MCP (Model Context Protocol) tools, and multiple train APIs (RailRadar + RailKit).

## 📁 Project Structure

```
train_mcp_server/
├── src/
│   ├── api/                    # API integrations
│   │   ├── train_api.py        # RailRadar, RailKit, IRCTC2 API wrappers
│   │   └── railkit_wrapper.js  # Node.js wrapper for RailKit SDK
│   ├── mcp/                    # MCP Server
│   │   ├── server.py           # FastMCP server with tools
│   │   └── tools.py            # MCP tool adapters for LangChain
│   ├── workflow/               # LangGraph workflow
│   │   └── orchestration.py    # Train recommendation workflow
│   ├── bot/                    # Discord bot
│   │   └── discord_bot.py      # Discord bot with slash commands
│   └── config/                 # Configuration
│       └── config.py           # API keys and settings
├── tests/                      # Test files
├── env5/                       # Python virtual environment
├── node_modules/               # Node.js dependencies
├── .env                        # Environment variables (API keys)
├── run_server.py               # Entry point for MCP server
├── run_bot.py                  # Entry point for Discord bot
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies (RailKit SDK)
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- Discord Bot Token
- RailRadar API Key
- RailKit API Key

### Installation

1. **Clone and navigate to project:**
   ```bash
   cd c:\train_mcp_server
   ```

2. **Activate virtual environment:**
   ```powershell
   .\env5\Scripts\Activate.ps1
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

5. **Configure environment variables:**
   Edit `.env` file:
   ```env
   RAILRADAR_API_KEY=your_railradar_key
   RAILKIT_API_KEY=your_railkit_key
   DISCORD_TOKEN=your_discord_token
   IRCTC2_API_KEY=your_irctc2_key
   ```

### Running the Bot

1. **Start MCP Server (in one terminal):**
   ```powershell
   .\env5\Scripts\python.exe run_server.py
   ```

2. **Start Discord Bot (in another terminal):**
   ```powershell
   .\env5\Scripts\python.exe run_bot.py
   ```

## 📋 Discord Commands

- `/train <query>` - Search for trains
  - Example: `/train query: Howrah to Bhubaneswar on 9th August budget 2000 class 3A`
- `/ping` - Check bot latency
- `/help` - Show help message

## 🔄 Workflow

1. **Extract constraints** - LLM extracts source, destination, date, budget, class from user query
2. **Resolve stations** - Convert station names to codes using RailRadar API
3. **Fetch trains** - Get train list from RailRadar API
4. **Time filter** - Filter by departure/arrival preferences
5. **Fetch seat data** - Get availability and fares from RailKit SDK (top 3 trains only)
6. **Budget filter** - Filter by budget and seat availability
7. **Rank trains** - Score trains based on multiple factors
8. **Generate recommendation** - Create user-friendly recommendation

## 🔑 API Integrations

### RailRadar API
- **Purpose:** Fetch train routes and schedules
- **Endpoint:** `https://railradar-api.rajivdubey.dev`
- **Usage:** Free tier

### RailKit SDK
- **Purpose:** Seat availability and fare lookup
- **Package:** `npm install railkit`
- **Usage:** Free tier (requires official Node.js SDK)
- **Optimization:** Only checks top 3 trains to reduce API calls

### IRCTC2 API (Fallback)
- **Purpose:** Backup when RailKit fails
- **Status:** Currently disabled due to reliability issues

## ⚙️ Configuration

### Key Settings

- **Max trains to check:** 3 (in `src/workflow/orchestration.py`)
- **API timeout:** 30-35 seconds
- **Date format:** YYYY-MM-DD (internal), DD-MM-YYYY (RailKit)
- **Class mapping:** Sleeper→SL, AC 3-Tier→3A, etc.

## 🧪 Testing

Run tests from the `tests/` directory:
```bash
python tests/test_scenarios.py
python tests/test_stations.py
```

## 📦 Dependencies

### Python
- `discord.py` - Discord bot framework
- `fastmcp` - MCP server framework  
- `langgraph` - Workflow orchestration
- `langchain` - LLM integration
- `requests` - HTTP client
- `python-dotenv` - Environment variables

### Node.js
- `railkit` - Official RailKit SDK

## 🐛 Troubleshooting

### Bot not connecting to Discord
- Check `DISCORD_TOKEN` in `.env`
- Verify bot has proper permissions in Discord Developer Portal

### MCP Server not starting
- Ensure `run_server.py` path is correct in `src/mcp/tools.py`
- Check Python virtual environment is activated

### RailKit API errors
- Verify API key is valid
- Free tier requires official SDK (not direct REST calls)
- Check network/firewall settings

## 📝 License

MIT

## 👤 Author

Sivam Singh
