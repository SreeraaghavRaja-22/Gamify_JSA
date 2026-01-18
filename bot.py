import discord
from discord.ext import commands
import logging
import config 
from sheets.client import get_client
from sheets import actions

# 1. Setup Intents 
intents = discord.Intents.default()
intents.message_content = True # Allows bot to read commands

bot = commands.Bot(command_prefix='!', intents=intents)

# 2. Startup Event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Bot is ready to process sheets!')

# 3. Commands:

# !process_event
@bot.command()
@commands.has_role("Officer")
# @commands.has_role("Officer") # Uncomment this later when you have roles set up
async def process_event(ctx, sheet_url: str, xp_amount: int):
    """
    Usage: !process_event [URL] [XP]
    Example: !process_event https://docs.google.com/spreadsheets/d/123... 40
    """

    await ctx.send(f"🔄 Processing event sheet... this might take a moment.")
    
    # Get the google sheet client
    client = get_client()
    
    # Run the logic from actions.py using SHEET_ID from config.py
    result_message = actions.process_event_data(
        client = client, 
        master_sheet_id = config.SHEET_ID, 
        event_sheet_url = sheet_url, 
        xp_amount = xp_amount
    )
    
    await ctx.send(result_message)

# !join
@bot.command()
async def join(ctx, email: str):
    """
    Usage: !join email@ufl.edu
    """

    client = get_client()

    result = actions.get_join(client, config.SHEET_ID, email, str(ctx.author.id))

    await ctx.send(result)

# !leaderboard
@bot.command()
async def leaderboard(ctx, *args):
    """
    Usage:
    !leaderboard
    !leaderboard 10
    !leaderboard all
    !leaderboard 10 all
    """

    client = get_client()

    top = 10
    include_board_members = False

    for arg in args:
        arg = arg.lower()

        if arg.isdigit():
            top = int(arg)
        elif arg == "all":
            include_board_members = True

    result = actions.get_leaderboard(client, config.SHEET_ID, top, include_board_members)

    await ctx.send(result)

# !xp 
@bot.command()
async def xp(ctx):
    """
    Usage: !xp 
    """

    client = get_client()

    result = actions.get_xp(client, config.SHEET_ID, str(ctx.author.id))

    await ctx.send(result) 

# quests


@bot.event
async def on_raw_reaction_add(payload):
    quest_channels = {
        config.DAILY_SUBMISSION_ID: config.DAILY_XP,
        config.WEEKLY_SUBMISSION_ID: config.WEEKLY_XP
    }

    if payload.channel_id not in quest_channels or str(payload.emoji) != config.APPROVE_EMOJI:
        return

    # Gets the member who reacted
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if member is None:
        member = await guild.fetch_member(payload.user_id)

    # Verifies the officer role 
    if not any(role.name == config.OFFICER_ROLE for role in member.roles):
        return # If not an officer, ignore reaction

    # Process the Quest
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    if message.author.bot:
        return

    # Awards XP sends message
    xp_to_give = quest_channels[payload.channel_id]
    client = get_client()
    result = actions.award_quest_xp(client, config.SHEET_ID, str(message.author.id), xp_to_give)
    
    response_message = (
        f"⚔️ **Quest Accomplished!** 🏯\n"
        f"Hello {message.author.mention}! An officer has verified your submission.\n"
        f"✨ **{result}**"
    )

    await channel.send(response_message)


# Handles permission errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ **Access Denied:** You do not have the 'Officer' role required to use this command.")
    else:
        # Log other errors to the terminal
        print(f"Error: {error}")

# 4. Run the Bot
bot.run(config.DISCORD_TOKEN)