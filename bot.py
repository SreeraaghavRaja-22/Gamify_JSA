import discord
from discord.ext import commands
import logging
import config 
from sheets.client import get_client
from sheets import actions

# client = get_client()
# sheet = client.open_by_key(config.SHEET_ID)

# # Access tabs.
# master_roster = sheet.worksheet("Master_Roster")
# attendance_logs = sheet.worksheet("Attendance_Logs")

# # Should print "Arisa is a bozo"
# print(sheet.worksheet("Master_Roster").row_values(1))

# 1. Setup Intents (Required for Discord.py 2.0+)
intents = discord.Intents.default()
intents.message_content = True # Allows bot to read commands

bot = commands.Bot(command_prefix='!', intents=intents)

# 2. Startup Event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Bot is ready to process sheets!')

# 3. The Command: !process_event
@bot.command()
# @commands.has_role("Officer") # Uncomment this later when you have roles set up
async def process_event(ctx, sheet_url: str, xp_amount: int):
    """
    Usage: !process_event [URL] [XP]
    Example: !process_event https://docs.google.com/spreadsheets/d/123... 40
    """
    await ctx.send(f"🔄 Processing event sheet... this might take a moment.")
    
    # Get the google sheet client
    client = get_client()
    
    # Run the logic from actions.py
    # This uses the SHEET_ID from your config.py
    result_message = actions.process_event_data(
        client = client, 
        master_sheet_id = config.SHEET_ID, 
        event_sheet_url = sheet_url, 
        xp_amount = xp_amount
    )
    
    await ctx.send(result_message)

@bot.command()
async def leaderboard(ctx, top: int = 10, board_member: str = None):
    """
    Usage:
    !leaderboard
    !leaderboard 10
    !leaderboard all
    !leaderboard 10 all
    """
    
    client = get_client()

    # Boolean parameters don't work well in Discord commands, so take board_member as a string and convert it to a boolean.
    include_board_members = board_member == "all"

    result = actions.get_leaderboard(client, config.SHEET_ID, top, include_board_members)

    await ctx.send(result)

# 4. Run the Bot
bot.run(config.DISCORD_TOKEN)