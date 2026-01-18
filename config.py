import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Quest Channels
DAILY_SUBMISSION_ID = 1462265730874478653  # Replace with actual ID
WEEKLY_SUBMISSION_ID = 1462265776105984030 # Replace with actual ID

DAILY_XP = 10
WEEKLY_XP = 20
OFFICER_ROLE = "Officer"
APPROVE_EMOJI = "✅"