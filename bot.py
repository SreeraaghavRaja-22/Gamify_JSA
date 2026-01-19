import discord
from discord.ext import commands
from discord import app_commands
import logging
import config 
from sheets.client import get_client
from sheets import actions
from wordle import wordle_actions

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

# Processing Events
@bot.tree.command(name="process_event", description="Adds attendance sheet url for certain event (only officers", guild=GUILD_ID)
@app_commands.default_permissions()
@app_commands.checks.has_role(config.OFFICER_ROLE_ID)
async def process_event(interaction: discord.Interaction, sheet_url: str, xp_amount: int):

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

# Join
@bot.tree.command(name="join", description="Joins the JSA Battle Pass!", guild=GUILD_ID)
async def join(interaction: discord.Interaction, email: str):

    client = get_client()

    result = actions.get_join(client, config.SHEET_ID, email, str(interaction.user.id))

    await interaction.response.send_message(result)

# Leaderboard
@bot.tree.command(name="leaderboard", description="Prints out the leaderboard", guild=GUILD_ID)
@app_commands.describe(type="Choose between Regular or Board members")
@app_commands.choices(type=[
    app_commands.Choice(name="Regular Members", value="regular"),
    app_commands.Choice(name="Board Members", value="board")
])
async def leaderboard(interaction: discord.Interaction, type: str = "regular", top: int = 10):
    await interaction.response.defer() 
    
    client = get_client()
    
    result = actions.get_leaderboard(client, config.SHEET_ID, top, mode=type)

    await interaction.followup.send(result)

# XP
@bot.tree.command(name="xp", description="Prints out your total XP!", guild=GUILD_ID)
async def xp(interaction: discord.Interaction):
    
    client = get_client()

    result = actions.get_xp(client, config.SHEET_ID, str(interaction.user.id))

    await interaction.response.send_message(result) 

# Quests
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

# Socials
@bot.tree.command(name="socials", description="This is a link to all of JSA's socials", guild=GUILD_ID)
async def socials(interaction: discord.Interaction):
    embed = discord.Embed(
        title = "JSA Socials",
        description="Tap a button to open a link",
    )
    await interaction.response.send_message(embed=embed, view=SocialsView())

# Shota
@bot.tree.command(name="shota", description="This is a dedication to JSA's Founder Shota Konno!", guild=GUILD_ID)
async def shota(interaction: discord.Interaction):
    response_message = "In winter of 2021, Shota Konno (c.o. 2025) founded the UF Japanese Student Association " \
    "along with Taise Miyazumi (c.o. 2024), Annika Joy Cruz (c.o. 2025), and Ellie Uchida-Prebor (c.o. 2025). " \
    "Shota served as president for three years, during which he oversaw JSA's first AASA participation, " \
    "two Undokai events, several banquets, and many other events. His biggest hope is for JSA to grow and continue to " \
    "follow its mission to provide a safe space for anyone and everyone to learn about Japanese culture!"
    await interaction.response.send_message(response_message)

# Claim_Wordle
@bot.tree.command(name="claim_wordle", description="Claim XP for completing Wordle (paste the Wordle share text).", guild=GUILD_ID)
async def claim_wordle(interaction: discord.Interaction, share_text: str):
    # parse the share text
    parsed = wordle_actions.parse_wordle_share(share_text)

    if not parsed:
        await interaction.response.send_message(
        "I couldn't find a valid header. Paste the line that looks like: 'Wordle 1674 3/6' plus the grid.", ephemeral=True)
        return
    
    # convert the parsed text to puzzle num and number of attempts
    puzzle, attempts = parsed

    # Wordle must be completed
    if attempts is None: 
        await interaction.response.send_message("Looks like this was X/6 (not completed). No XP rewarded.", ephemeral = True) 
        return
    
    client = get_client()
    
    # Prevents double claim error for the same puzzle
    if actions.wordle_claim_exists(client, config.SHEET_ID, puzzle, interaction.user.id):
        await interaction.response.send_message("You already claimed this Wordle.", ephemeral=True)
        return

    # Log first so we don't double award if an error occurs
    actions.log_wordle_claim(client, config.SHEET_ID, puzzle, interaction.user.id)

    # set XP_REWARD 
    XP_REWARD = 10

    # Reward the user with XP_REWARD XP
    result = actions.award_quest_xp(client, config.SHEET_ID, interaction.user.id, XP_REWARD)
    
    # Send the message that the XP has been rewarded
    await interaction.response.send_message(f"✅ Wordle {puzzle} completed. +{XP_REWARD} XP\n{result}", ephemeral = True)

# 4. Run the Bot
bot.run(config.DISCORD_TOKEN)