╔══════════════════════════════════════════════════════════════════════════════╗
║                       DISCORD BOT SETUP GUIDE                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

So you want to get this bot running on Discord? Here's how to do it step by 
step.


┌─ WHAT YOU'LL NEED ───────────────────────────────────────────────────────────┐

Make sure you have these installed:
  - Python 3.8 or newer
  - Node.js (the bot needs it for RailKit)
  - The virtual environment set up (the env5 folder)
  - All the dependencies installed (pip install -r requirements.txt and npm install)


╔══════════════════════════════════════════════════════════════════════════════╗
║                     CREATING YOUR DISCORD BOT                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─ STEP 1: MAKE A DISCORD APPLICATION ────────────────────────────────────────┐

Head over to the Discord Developer Portal and log in:
  -> https://discord.com/developers/applications

Click "New Application" and give it a name - something like "Train Bot" or 
whatever you want. Hit Create.


┌─ STEP 2: TURN IT INTO A BOT ────────────────────────────────────────────────┐

Go to the "Bot" tab on the left sidebar.

Click "Add Bot" and confirm. Now you have a bot!

You'll see some settings here. The important one is "Privileged Gateway Intents":
  • Message Content Intent - turn this on if you want the bot to read messages 
    (optional for now since we're using slash commands)
  • The other two are optional

Now click "Reset Token" and copy the token that appears. This is basically 
your bot's password - don't share it with anyone or post it online.


┌─ STEP 3: SAVE YOUR TOKEN ───────────────────────────────────────────────────┐

Open the .env file in your project folder. You'll see a line that says:

  DISCORD_TOKEN=your_discord_bot_token_here

Replace that with your actual token:

  DISCORD_TOKEN=paste_your_token_here

Save the file.


┌─ STEP 4: INVITE THE BOT TO YOUR SERVER ─────────────────────────────────────┐

Back in the Developer Portal, go to "OAuth2" then "URL Generator".

Select these scopes:
  - bot
  - applications.commands (important - this is what makes slash commands work)

Then scroll down and select these permissions:
  - Send Messages
  - Embed Links
  - Read Message History

Copy the URL at the bottom, paste it in your browser, and select which server 
you want to add the bot to. Click Authorize.

Your bot should now appear in your server (it'll be offline until you start it).


╔══════════════════════════════════════════════════════════════════════════════╗
║                       STARTING EVERYTHING UP                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

You need to run two things for the bot to work:

┌─ FIRST TERMINAL - START THE MCP SERVER ─────────────────────────────────────┐

  .\env5\Scripts\Activate.ps1
  .\env5\Scripts\python.exe run_server.py

Wait until you see "MCP tools loaded successfully!"

┌─ SECOND TERMINAL - START THE BOT ───────────────────────────────────────────┐

  .\env5\Scripts\Activate.ps1
  .\env5\Scripts\python.exe run_bot.py

When you see "is now online!" your bot is ready.


╔══════════════════════════════════════════════════════════════════════════════╗
║                          USING THE BOT                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

The bot uses slash commands. Here's what you can do:

/train - Search for trains. Just describe what you want in plain English:
  ▸ Mumbai to Delhi tomorrow budget 5000
  ▸ Sleeper train from Kolkata to Bangalore next Friday
  ▸ AC 3 Tier from Chennai to Hyderabad on August 20th

/ping - Check if the bot is alive and see response time

/help - Get help and see more examples

To use a slash command, just type / in Discord and the bot's commands will 
pop up. Click on one and fill in what it asks for.


┌─ HOW THE BOT WORKS ──────────────────────────────────────────────────────────┐

When you send a train query, here's what happens:

  -> The bot uses AI to figure out what you're asking for (where from, where to, 
    when, how much money, what class)
  -> It searches for stations and trains using the RailRadar API
  -> It checks seat availability for the best trains using RailKit
  -> It filters everything based on your budget and preferences
  -> Finally, it picks the best train and tells you why

The whole thing takes about 5-10 seconds.


╔══════════════════════════════════════════════════════════════════════════════╗
║                       WHEN THINGS GO WRONG                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

! Slash commands don't show up

Make sure you selected the applications.commands scope when you invited the 
bot. If you didn't, you'll need to kick the bot and re-invite it with the 
right permissions.

! Bot is online but doesn't respond

Did you start the MCP server first? The bot needs it to work. Always run 
run_server.py before run_bot.py.

! "No trains found" for routes that exist

Try using full station names instead of abbreviations. For example, "New Delhi" 
instead of "Delhi". Also double-check your date is in the future.

! RailKit API errors

Make sure you ran npm install and that your RailKit API key is valid. The free 
tier needs the official SDK to work.

! Bot crashes on startup

Check that all your API keys are set in the .env file. If one is missing, the 
bot will complain and exit.


┌─ WHAT'S ACTUALLY HAPPENING BEHIND THE SCENES ───────────────────────────────┐

The Discord bot is the front-end that you interact with.
  ↓
It sends your query to a LangGraph workflow that breaks down what you want.
  ↓
The workflow calls the MCP server to get train data.
  ↓
The MCP server talks to the actual APIs (RailRadar, RailKit).
  ↓
Everything flows back up and you get a nice recommendation.

We only check the top 3 trains for seat availability to save API calls. This 
makes things faster and prevents hitting rate limits on the free tier.


┌─ API KEYS YOU'LL NEED ───────────────────────────────────────────────────────┐

RailRadar API Key
  -> Get this from https://api.railradar.in/ (free tier available)

RailKit API Key
  -> Get this from https://railkit-api.rajivdubey.dev/ (free tier available)

IRCTC2 API Key
  -> Optional, only needed as a backup

Put all of these in your .env file.


┌─ TIPS ───────────────────────────────────────────────────────────────────────┐

• The bot understands natural language pretty well. You don't need to format 
  things perfectly.

• If the bot says it's missing information, just try again with more details.

• Budget is required - the bot uses it to filter trains.

• Date can be written many ways: "tomorrow", "next Monday", "2026-08-20", 
  "15th August", etc.

• Class names are flexible: "sleeper", "SL", "3A", "AC 3 Tier" all work.


┌─ GETTING HELP ───────────────────────────────────────────────────────────────┐

If something's not working:

  [1] Check both terminal windows for error messages
  [2] Make sure the MCP server started successfully before the bot
  [3] Verify all your API keys are in the .env file
  [4] Try restarting both the server and bot
  [5] Check that Node.js and npm are installed (node --version and npm --version)

Still stuck? Double-check the main README.md for more details.


╔══════════════════════════════════════════════════════════════════════════════╗
║                             THAT'S IT!                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

You should be good to go. Start asking your bot for train recommendations and 
see what it comes up with!
