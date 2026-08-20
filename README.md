╔══════════════════════════════════════════════════════════════════════════════╗
║                     TRAIN RECOMMENDATION DISCORD BOT                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

This is a Discord bot that helps you find the best trains for your journey. 
It uses AI to understand what you're looking for and searches through multiple 
train APIs to give you personalized recommendations.


┌─ WHAT'S INSIDE ──────────────────────────────────────────────────────────────┐

The project is organized into folders based on what they do:

  src/api/      - Connects to RailRadar and RailKit APIs to fetch train data
  src/server/   - MCP server that exposes train search tools
  src/workflow/ - The brain of the bot - figures out what you want and finds the best trains
  src/bot/      - The Discord interface where you interact with the bot
  src/config/   - Stores API keys and settings

You'll also find run_server.py and run_bot.py in the root - these are what 
you run to start everything.


┌─ GETTING STARTED ────────────────────────────────────────────────────────────┐

Before you can use the bot, you'll need:
  • Python 3.13 or newer
  • Node.js 18 or newer
  • A Discord bot token (from Discord Developer Portal)
  • API keys for RailRadar and RailKit


┌─ SETTING EVERYTHING UP ──────────────────────────────────────────────────────┐

First, activate your Python virtual environment:

  .\env5\Scripts\Activate.ps1

Install the Python packages:

  pip install -r requirements.txt

Install Node.js dependencies (needed for RailKit):

  npm install

Copy .env.example to .env and fill in your API keys. It should look something 
like this:

  RAILRADAR_API_KEY=your_key_here
  RAILKIT_API_KEY=your_key_here
  DISCORD_TOKEN=your_bot_token
  IRCTC2_API_KEY=optional_backup_key


┌─ RUNNING THE BOT ────────────────────────────────────────────────────────────┐

You need two terminal windows:

-> Terminal 1 - Start the MCP server first:

  .\env5\Scripts\python.exe run_server.py

-> Terminal 2 - Then start the Discord bot:

  .\env5\Scripts\python.exe run_bot.py

The bot won't work without the MCP server running, so always start that first.


┌─ USING THE BOT ──────────────────────────────────────────────────────────────┐

Once the bot is online in your Discord server, you can use these commands:

/train - This is the main command. Just describe what you're looking for:
  • Mumbai to Delhi tomorrow, budget 5000
  • Kolkata to Chennai on August 15th, AC 3 Tier class
  • Cheap sleeper train from Bangalore to Hyderabad next week

/ping - Check if the bot is responding

/help - Get help and see examples


┌─ HOW IT WORKS ───────────────────────────────────────────────────────────────┐

When you send a query, here's what happens:

  [1] The bot uses AI to understand what you're asking for (source, destination, 
      date, budget, etc.)
  [2] It converts station names to codes (like Mumbai to MMCT)
  [3] Searches for all trains on that route
  [4] Filters them based on your time preferences
  [5] Checks seat availability for the top 3 trains (to save API calls)
  [6] Filters by your budget
  [7] Ranks them and picks the best one
  [8] Explains why it chose that train

The whole thing takes about 5-10 seconds depending on how many trains it needs 
to check.


┌─ ABOUT THE APIS ─────────────────────────────────────────────────────────────┐

RailRadar API is used to search for stations and get train schedules. It's 
free and pretty reliable.

RailKit SDK gives us real-time seat availability and fares. We use their 
official Node.js SDK because their free tier requires it. The bot only checks 
the top 3 trains to avoid hitting rate limits.

IRCTC2 API is there as a backup but isn't actively used right now.


┌─ CONFIGURATION NOTES ────────────────────────────────────────────────────────┐

The bot is set to check only the top 3 trains for seat availability. You can 
change this in src/workflow/orchestration.py if you want, but more trains 
means more API calls and longer wait times.

Date formats can be natural language like "tomorrow" or "next Friday" - the 
AI figures it out. Internally everything uses YYYY-MM-DD format.

Class names are flexible - you can say "sleeper", "3A", "AC 3 Tier", whatever 
makes sense.


┌─ COMMON ISSUES ──────────────────────────────────────────────────────────────┐

! Bot doesn't respond to commands

  Make sure you invited the bot with the applications.commands scope. Regular 
  bot scope isn't enough for slash commands.

! "MCP client not initialized" error

  The bot can't reach the MCP server. Make sure run_server.py is running 
  before you start the bot.

! RailKit API errors

  Check that your API key is valid. Also make sure Node.js is installed and 
  you ran npm install. The SDK won't work without it.

! Bot says "no trains found" for valid routes

  Try using full station names. Sometimes shorter names don't match. Also 
  check that the date is in the future.


┌─ HOW EVERYTHING CONNECTS ───────────────────────────────────────────────────┐

Think of it like this:

  You type a command in Discord 
    ↓
  Discord bot receives it 
    ↓
  Sends to LangGraph workflow 
    ↓
  Workflow asks MCP server for data 
    ↓
  MCP server calls Train APIs 
    ↓
  Data flows back up the chain 
    ↓
  You get a recommendation

The MCP layer is what lets the workflow call the APIs without knowing the 
implementation details. It's basically a clean interface.


┌─ TECH STACK ─────────────────────────────────────────────────────────────────┐

Python side:
  ▸ discord.py for the Discord bot
  ▸ fastmcp for the MCP server
  ▸ langgraph for the workflow logic
  ▸ langchain-ollama for AI/LLM integration
  ▸ requests for API calls

Node.js side:
  ▸ railkit package (official SDK)


┌─ LICENSE ────────────────────────────────────────────────────────────────────┐

MIT - feel free to use this however you want.


┌─ AUTHOR ─────────────────────────────────────────────────────────────────────┐

Built by Sivam Singh
