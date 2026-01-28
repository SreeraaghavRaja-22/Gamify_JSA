<!-- Badges -->
<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://discordpy.readthedocs.io/"><img src="https://img.shields.io/badge/Discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord.py" /></a>
  <a href="https://developers.google.com/sheets/api"><img src="https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=googlesheets&logoColor=white" alt="Google Sheets" /></a>
  <a href="https://gspread.readthedocs.io/"><img src="https://img.shields.io/badge/gspread-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="gspread" /></a>
  <a href="https://www.digitalocean.com/"><img src="https://img.shields.io/badge/DigitalOcean-0080FF?style=for-the-badge&logo=digitalocean&logoColor=white" alt="DigitalOcean" /></a>
</p>

---

<h1 align="center">🏯 Gamify JSA</h1>

<p align="center">
  <strong>Level up your JSA experience.</strong>
</p>

<p align="center">
  A Discord bot that gamifies participation for the UF Japanese Student Association with an XP-based progression system, quests, leaderboards, and more.
</p>

<!-- TODO: Add screenshot or demo GIF here -->
<!-- <p align="center">
  <img src="./demo.gif" alt="Gamify JSA Demo" width="600" />
</p> -->

---

## Overview

**Gamify JSA** transforms club participation into an engaging RPG-like experience. Members earn XP by attending events, completing daily and weekly quests, and even playing Wordle. As they accumulate XP, they progress through ranks — from humble **Newcomer** all the way to **Honorary JSA Board**.

Officers can easily process event attendance through Google Sheets integration, and the bot automatically awards XP and updates member ranks. The quest system keeps members engaged between events with fun challenges verified by the officer team.

---

## How It Works

1. **Join the System** — Members use `/join` with their email to link their Discord account to the XP roster.
2. **Attend Events** — Officers process attendance sheets, and XP is automatically awarded to all attendees.
3. **Complete Quests** — Daily and weekly quests are posted automatically. Submit proof and get officer approval for XP.
4. **Play Wordle** — Paste your Wordle results with `/claim_wordle` to earn bonus XP.
5. **Climb the Ranks** — Check your progress with `/xp` and compete on the `/leaderboard`.

---

## Rank Progression

<p align="center">

| XP Required | Rank |
|:-----------:|:-----|
| 0 | 🌱 Newcomer |
| 50 | 📚 Daiyo's Classmate |
| 150 | 🤝 Daiyo's Friend |
| 300 | 🐕 Daiyo's Pet |
| 500 | ⭐ JSA Regular |
| 750 | 🎌 JSA Otaku |
| 1050 | 👑 Honorary JSA Board |

</p>

---

## Key Features

- **XP & Rank System** — Earn XP from events, quests, and Wordle. Automatically rank up as you progress.
- **Event Processing** — Officers paste a Google Sheets attendance URL and XP is awarded to all attendees instantly.
- **Daily & Weekly Quests** — Automated quest announcements with officer-verified submissions.
- **Wordle Integration** — Claim XP daily by sharing your Wordle results.
- **Dual Leaderboards** — Separate rankings for regular members and board members.
- **Auto-Enrollment** — New event attendees are automatically added to the roster.
- **Duplicate Protection** — Prevents double-processing of events and double-claiming of Wordle puzzles.

---

## Tech Stack

### Bot Framework
- **Python 3.8+** — Core programming language
- **Discord.py** — Discord API wrapper with slash commands
- **python-dotenv** — Environment variable management

### Data Storage
- **Google Sheets API** — Cloud-based data storage for rosters, quests, and logs
- **gspread** — Python client for Google Sheets
- **google-auth** — Service account authentication

### Deployment
- **DigitalOcean Droplet** — Ubuntu VPS for 24/7 hosting
- **systemd** — Process management and auto-restart

---

## Getting Started

### Prerequisites

- Python 3.8+
- Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))
- Google Cloud Service Account with Sheets API enabled
- Google Sheet set up with required worksheets

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/YOUR_USERNAME/Gamify_JSA.git
   cd Gamify_JSA
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   Create a `.env` file in the root directory:

   ```env
   DISCORD_TOKEN=your_discord_bot_token
   GOOGLE_SHEET_ID=your_google_sheet_id
   GUILD_NUM=your_discord_server_id
   ```

5. Add your Google Cloud service account credentials as `credentials.json` in the root directory.

6. Set up your Google Sheet with these worksheets:

   | Worksheet | Purpose |
   |-----------|---------|
   | `Master_Roster` | Member data (Name, Email, Year, Discord_ID, Total_XP, Rank, Board_Member) |
   | `Attendance_Logs` | Tracks processed event sheets |
   | `Daily_Quests` | Quest Name, Description, Objective, Verification Method, Last_Used |
   | `Weekly_Quests` | Same structure as Daily_Quests |
   | `Wordle_Claims` | Tracks claimed Wordle puzzles |
   | `Board_Roster` | List of board member emails |

7. Run the bot:

   ```bash
   python bot.py
   ```

---

## Commands

### Member Commands

| Command | Description |
|---------|-------------|
| `/join <email>` | Register your Discord account with the JSA XP system |
| `/xp` | Check your current XP and rank |
| `/leaderboard [type] [top]` | View the leaderboard (regular or board members) |
| `/claim_wordle <share_text>` | Claim XP for completing Wordle |
| `/socials` | Get links to JSA social media |
| `/shota` | Learn about JSA's founder |

### Officer Commands

| Command | Description |
|---------|-------------|
| `/process_event <sheet_url> <xp_amount>` | Process an attendance sheet and award XP |
| `/test_quest <type>` | Test a quest announcement |
| `/refresh_quest <type>` | Force a new quest announcement |
| `/post_specific_quest <type> <name>` | Post a specific quest by name |
| `/sync_board_members` | Sync board member status from Board_Roster |

---

## Project Structure

```
Gamify_JSA/
├── bot.py                # Main Discord bot with commands and event handlers
├── config.py             # Configuration and environment variables
├── requirements.txt      # Python dependencies
├── credentials.json      # Google Cloud service account (not in repo)
├── .env                  # Environment variables (not in repo)
├── sheets/
│   ├── client.py         # Google Sheets authentication
│   └── actions.py        # Sheet operations (XP, leaderboards, quests)
└── wordle/
    └── wordle_actions.py # Wordle share text parsing
```

---

## Configuration

Edit `config.py` to customize:

| Setting | Description |
|---------|-------------|
| `DAILY_XP` / `WEEKLY_XP` / `WORDLE_XP` | XP rewards for different activities |
| `QUEST_CHANNEL_ID` | Channel for quest announcements |
| `DAILY_SUBMISSION_ID` / `WEEKLY_SUBMISSION_ID` | Channels for quest submissions |
| `OFFICER_ROLE` / `OFFICER_ROLE_ID` | Role required for admin commands |
| `APPROVE_EMOJI` | Emoji used to approve quest submissions (default: ✅) |

---

## Deployment

The bot is deployed on a **DigitalOcean Droplet** running Ubuntu, managed with **systemd** for automatic restarts and boot persistence.

### Useful Server Commands

| Command | Description |
|---------|-------------|
| `systemctl status jsabot` | Check if bot is running |
| `systemctl restart jsabot` | Restart the bot |
| `systemctl stop jsabot` | Stop the bot |
| `journalctl -u jsabot -f` | View live logs |
| `journalctl -u jsabot -n 100` | View last 100 log lines |

### Updating the Bot

```bash
cd ~/Gamify_JSA
git pull
systemctl restart jsabot
```

---

## Credits

- **[Discord.py](https://discordpy.readthedocs.io/)** — Discord API wrapper
- **[gspread](https://gspread.readthedocs.io/)** — Google Sheets Python client
- **[DigitalOcean](https://www.digitalocean.com/)** — Cloud hosting
- **Cursor** — AI-powered IDE

---

## Future Roadmap

- [ ] Quest streak tracking with bonus XP
- [ ] `/profile` command with detailed stats
- [ ] Celebratory message for ranking up
- [ ] GitHub Actions for automated deployment

---

<p align="center">
  Made with ❤️ for the UF Japanese Student Association
</p>
