import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GUILD_ID = os.getenv("GUILD_NUM")

# Quest Channels
DAILY_SUBMISSION_ID = 1462265730874478653  # Replace with actual ID
WEEKLY_SUBMISSION_ID = 1462265776105984030 # Replace with actual ID

DAILY_XP = 10
WEEKLY_XP = 20
OFFICER_ROLE = "Officer"
APPROVE_EMOJI = "✅"

INSTAGRAM = "https://www.instagram.com/uf_jsa/"
LINKTREE = "https://linktr.ee/uf.jsa?utm_source=ig&utm_medium=social&utm_content=link_in_bio"
CALENDAR = "https://calendar.google.com/calendar/embed?src=secretary.ufjsa%40gmail.com&ctz=America%2FNew_York"