import discord
from discord.ext import commands
import logging
import config 
from sheets.client import get_client
from sheets import actions

# 1. Setup Intents 
intents = discord.Intents.default()
intents.message_content = True # Allows bot to read commands

# 2. Startup Event
class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print('Bot is ready to process sheets!')
        try:
            guild = discord.Object(id = config.GUILD_ID)
            synced = await self.tree.sync(guild = guild)
            print(f"Synced {len(synced)} commands to guild")

        except Exception as e:
            print(f"Errors syncing commands: {e}")

bot = Client(command_prefix="!", intents=intents)
GUILD_ID = discord.Object(id = config.GUILD_ID)

# 3. Commands:

# !process_event
@bot.tree.command(name="process_event", description="add attendance sheet url for certain event", guild=GUILD_ID)
@commands.has_role("Officer")
# @commands.has_role("Officer") # Uncomment this later when you have roles set up
async def process_event(interaction: discord.Interaction, sheet_url: str, xp_amount: int):
    """
    Usage: !process_event [URL] [XP]
    Example: !process_event https://docs.google.com/spreadsheets/d/123... 40
    """

    await interaction.response.send_message(f"🔄 Processing event sheet... this might take a moment.")
    
    # Get the google sheet client
    client = get_client()
    
    # Run the logic from actions.py using SHEET_ID from config.py
    result_message = actions.process_event_data(
        client = client, 
        master_sheet_id = config.SHEET_ID, 
        event_sheet_url = sheet_url, 
        xp_amount = xp_amount
    )
    
    await interaction.followup.send(result_message)

# !join
@bot.tree.command(name="join", description="join the JSA Bot", guild=GUILD_ID)
async def join(interaction: discord.Interaction, email: str):
    """
    Usage: !join email@ufl.edu
    """

    client = get_client()

    result = actions.get_join(client, config.SHEET_ID, email, str(interaction.user.id))

    await interaction.response.send_message(result)

# !leaderboard
@bot.tree.command(name="leaderboard", description="print the leaderboard", guild=GUILD_ID)
async def leaderboard(interaction: discord.Interaction, top: int = 10, include_board_members: bool = False):
    """
    Usage:
    !leaderboard
    !leaderboard 10
    !leaderboard all
    !leaderboard 10 all
    """

    client = get_client()

    result = actions.get_leaderboard(client, config.SHEET_ID, top, include_board_members)

    await interaction.response.send_message(result)

# !xp 
@bot.tree.command(name="xp", description="print out your xp", guild=GUILD_ID)
async def xp(interaction: discord.Interaction):
    """
    Usage: !xp 
    """

    client = get_client()

    result = actions.get_xp(client, config.SHEET_ID, str(interaction.user.id))

    await interaction.response.send_message(result) 

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
@bot.tree.error
async def on_command_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRole):
        await interaction.response.send_message("❌ **Access Denied:** You do not have the 'Officer' role required to use this command.", ephemeral=True)
    else:
        # Log other errors to the terminal
        print(f"Error: {error}")


class SocialsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="INSTAGRAM", style = discord.ButtonStyle.blurple, url=config.INSTAGRAM))
        self.add_item(discord.ui.Button(label="LINKTREE", style=discord.ButtonStyle.red, url=config.LINKTREE))
        self.add_item(discord.ui.Button(label="JSA CALENDAR", style=discord.ButtonStyle.green, url=config.CALENDAR))

@bot.tree.command(name="socials", description="This is a link to all of JSA's socials", guild=GUILD_ID)
async def socials(interaction: discord.Interaction):
    embed = discord.Embed(
        title = "JSA Socials",
        description="Tap a button to open a link",
    )
    await interaction.response.send_message(embed=embed, view=SocialsView())

# 4. Run the Bot
bot.run(config.DISCORD_TOKEN)