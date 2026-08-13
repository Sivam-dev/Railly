#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from src.bot.discord_bot import bot, DISCORD_TOKEN
    
    print("Starting Discord bot with slash commands...")
    print("Make sure DISCORD_TOKEN is set in your .env file")
    print("=" * 60)
    print("Slash Commands:")
    print("  /train <query>  - Search for trains")
    print("  /ping           - Check bot latency")
    print("  /help           - Show help")
    print("=" * 60)
    
    bot.run(DISCORD_TOKEN)
