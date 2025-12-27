import discord
from discord.ext import commands
import logging
import config 
from sheets.client import get_client
from sheets import actions

# Setup Intents
intents = discord.Intents.default()
intents.message_content = True # Allows bot to read commands

bot = commands.Bot(command_prefix='!', intents=intents)

# Startup Event
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

# 4. COMMAND: !join
@bot.command()
async def join(ctx, email: str):
    """
    Usage: !join email@ufl.edu
    Links your Discord account to your JSA Email.
    """
    client = get_client()

    # We pass the author's ID so we can link it in the sheet
    result = actions.get_join(
        client=client,
        master_sheet_id=config.SHEET_ID,
        email=email,
        discord_id=str(ctx.author.id)
    )
    
    await ctx.send(result)

# 5. COMMAND: !leaderboard
@bot.command()
async def leaderboard(ctx, *args):
    """
    Usage:
    !leaderboard        (Top 10)
    !leaderboard 20     (Top 20)
    !leaderboard all    (Includes Board Members)
    """
    client = get_client()
    
    # Default settings
    top = 10
    include_board_members = False

    # Parse arguments (e.g., "all", "20")
    for arg in args:
        arg = arg.lower()
        if arg.isdigit():
            top = int(arg)
        elif arg == "all":
            include_board_members = True

    result = actions.get_leaderboard(
        client=client, 
        master_sheet_id=config.SHEET_ID, 
        top=top, 
        include_board_members=include_board_members
    )
    
    await ctx.send(result)

# 6. COMMAND: !xp
@bot.command()
async def xp(ctx):
    """
    Usage: !xp 
    Shows your current rank and point total.
    """
    client = get_client()

    result = actions.get_xp(
        client=client,
        master_sheet_id=config.SHEET_ID,
        discord_id=str(ctx.author.id)
    )

    await ctx.send(result)

# 7. Run the Bot
if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)