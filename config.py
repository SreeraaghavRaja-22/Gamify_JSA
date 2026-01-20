import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GUILD_ID = os.getenv("GUILD_NUM")

# Quest Channels
DAILY_SUBMISSION_ID = 1462265730874478653  # Replace with actual ID
WEEKLY_SUBMISSION_ID = 1462265776105984030 # Replace with actual ID

DAILY_XP = 4
WEEKLY_XP = 18
WORDLE_XP = 1

OFFICER_ROLE = "Officer"
OFFICER_ROLE_ID = 1462266913684979893
APPROVE_EMOJI = "✅"

INSTAGRAM = "https://www.instagram.com/uf_jsa/"
LINKTREE = "https://linktr.ee/uf.jsa?utm_source=ig&utm_medium=social&utm_content=link_in_bio"
CALENDAR = "https://calendar.google.com/calendar/u/0?cid=YmViZDVhYTNhYzFiMTEwOTIzZWUyZGM1NTkwZDg4ZjA1NTI2Njk1NDA3YzA0Yjk4YmIxMzU4YWIzZmEwYmYwZkBncm91cC5jYWxlbmRhci5nb29nbGUuY29t"