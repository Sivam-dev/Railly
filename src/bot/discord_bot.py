import discord
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv
from src.workflow.orchestration import build_train_recommendation_graph

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in .env file!")

intents = discord.Intents.default()
intents.message_content = True

class TrainBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.train_graph = None
    
    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced with Discord!")

bot = TrainBot()

@bot.event
async def on_ready():
    print(f"{bot.user} is now online!")
    print(f"Connected to {len(bot.guilds)} server(s)")
    
    print("Building train recommendation workflow...")
    try:
        bot.train_graph = build_train_recommendation_graph()
        print("Workflow ready!")
        print("\nUse /train in Discord to search for trains!")
    except Exception as e:
        print(f"Failed to build workflow: {e}")
        print("Bot may not function correctly")
        import traceback
        traceback.print_exc()

@bot.tree.command(name="train", description="Search for train recommendations")
@app_commands.describe(query="Your train search query (e.g., 'Mumbai to Delhi tomorrow, budget 5000')")
async def train_command(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)
    try:
        initial_state = {
            "user_query": query,
            "source": None,
            "destination": None,
            "journey_date": None,
            "budget": None,
            "preferred_departure": None,
            "preferred_arrival": None,
            "preferred_class": None,
            "trains": [],
            "budget_filtered_trains": [],
            "alternative_class_trains": [],
            "time_filtered_trains": [],
            "ranked_trains": [],
            "recommended_train": None,
            "final_response": None,
            "follow_up_question": None,
            "recommendation": None
        }
        result = await bot.train_graph.ainvoke(initial_state)
        if "__interrupt__" in result:
            embed = discord.Embed(
                title="Need More Information",
                description="I couldn't extract all the required information from your query.",
                color=discord.Color.orange()
            )
            embed.add_field(name="What I understood:", value="", inline=False)
            if result.get("source"):
                embed.add_field(name="From", value=result["source"], inline=True)
            if result.get("destination"):
                embed.add_field(name="To", value=result["destination"], inline=True)
            if result.get("journey_date"):
                embed.add_field(name="Date", value=result["journey_date"], inline=True)
            if result.get("budget"):
                embed.add_field(name="Budget", value=f"Rs.{result['budget']}", inline=True)
            if result.get("preferred_class"):
                embed.add_field(name="Class", value=result["preferred_class"], inline=True)
            embed.add_field(
                name="Please provide:",
                value="Try including: source station, destination, date, budget, and class preference",
                inline=False
            )
            embed.add_field(
                name="Example:",
                value="`/train query: Mumbai to Delhi on 2026-08-20, budget 5000, AC 3 Tier`",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return
        final_response = result.get("final_response", "No recommendation available")
        if result.get("recommended_train"):
            train = result["recommended_train"]
            embed = discord.Embed(
                title="Train Recommendation Found",
                description=f"Here's the best train for your journey:",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Train", 
                value=f"**{train.get('trainNumber', 'N/A')}** - {train.get('trainName', 'N/A')}", 
                inline=False
            )
            embed.add_field(name="From", value=result["source"], inline=True)
            embed.add_field(name="To", value=result["destination"], inline=True)
            embed.add_field(name="Date", value=result["journey_date"], inline=True)
            if "departure" in train:
                embed.add_field(name="Departure", value=train["departure"], inline=True)
            if "arrival" in train:
                embed.add_field(name="Arrival", value=train["arrival"], inline=True)
            if "duration" in train:
                embed.add_field(name="Duration", value=train["duration"], inline=True)
            embed.add_field(name="Fare", value=f"Rs.{train.get('fare', 'N/A')}", inline=True)
            embed.add_field(name="Class", value=train.get('class', result.get("preferred_class", "N/A")), inline=True)
            if result.get("recommendation"):
                embed.add_field(name="Recommendation", value=result["recommendation"], inline=False)
            embed.set_footer(text="Train Recommendation System")
        else:
            embed = discord.Embed(
                title="No Trains Found",
                description=final_response,
                color=discord.Color.red()
            )
            embed.add_field(name="From", value=result.get("source", "N/A"), inline=True)
            embed.add_field(name="To", value=result.get("destination", "N/A"), inline=True)
            embed.add_field(name="Date", value=result.get("journey_date", "N/A"), inline=True)
            embed.add_field(name="Budget", value=f"Rs.{result.get('budget', 'N/A')}", inline=True)
            embed.add_field(name="Class", value=result.get("preferred_class", "N/A"), inline=True)
            trains_found = len(result.get("trains", []))
            budget_filtered = len(result.get("budget_filtered_trains", []))
            time_filtered = len(result.get("time_filtered_trains", []))
            embed.add_field(
                name="Search Stats",
                value=f"Found {trains_found} trains → {budget_filtered} within budget → {time_filtered} matching time preferences",
                inline=False
            )
            embed.add_field(
                name="Suggestions:",
                value="- Try increasing your budget\n- Choose a different date\n- Select a different class",
                inline=False
            )
            embed.set_footer(text="Try adjusting your criteria")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="Error",
            description=f"An error occurred while processing your request:\n```{str(e)}```",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=error_embed)
        print(f"Error in train command: {e}")
        import traceback
        traceback.print_exc()

@bot.tree.command(name="ping", description="Check bot latency")
async def ping_command(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=discord.Color.blue()
    )
    embed.add_field(name="Status", value="Online and ready!", inline=False)
    embed.add_field(name="MCP Server", value="Connected", inline=True)
    embed.add_field(name="Workflow", value="Ready", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show help and usage information")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Train Recommendation Bot - Help",
        description="I can help you find the best trains for your journey!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Commands",
        value=(
            "`/train <query>` - Search for trains\n"
            "`/ping` - Check bot latency\n"
            "`/help` - Show this help message"
        ),
        inline=False
    )
    embed.add_field(
        name="Example Queries",
        value=(
            "- `/train query: Mumbai to Delhi tomorrow with budget 5000`\n"
            "- `/train query: Chennai to Bangalore on 2026-08-20, AC 3 Tier`\n"
            "- `/train query: Sleeper class train from Kolkata to Mumbai next week, budget 3000`"
        ),
        inline=False
    )
    embed.add_field(
        name="What to include:",
        value=(
            "- **Source station** (e.g., Mumbai, Delhi)\n"
            "- **Destination station**\n"
            "- **Date** (YYYY-MM-DD format preferred)\n"
            "- **Budget** (in rupees)\n"
            "- **Class preference** (optional: Sleeper, 3A, 2A, etc.)\n"
            "- **Time preference** (optional: morning, evening)"
        ),
        inline=False
    )
    embed.set_footer(text="Powered by LangGraph & MCP")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error in event {event}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    print("Starting Discord bot with slash commands...")
    print("Make sure DISCORD_TOKEN is set in your .env file")
    print("\n" + "="*60)
    print("Slash Commands:")
    print("  /train <query>  - Search for trains")
    print("  /ping           - Check bot latency")
    print("  /help           - Show help")
    print("="*60 + "\n")
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Failed to start bot: {e}")
        print("\nMake sure:")
        print("  1. DISCORD_TOKEN is set in .env")
        print("  2. Bot has proper permissions")
        print("  3. Message Content Intent is enabled in Discord Developer Portal")
