# Gamify JSA

A Discord bot that gamifies participation for the UF Japanese Student Association (JSA) with an XP-based progression system, quests, and leaderboards.

## Features

- **XP System**: Members earn XP by attending events, completing quests, and playing Wordle
- **Rank Progression**: Automatic rank upgrades based on XP thresholds (Newcomer → Honorary JSA Board)
- **Event Processing**: Officers can process Google Sheets attendance data to award XP to attendees
- **Daily & Weekly Quests**: Automated quest announcements with officer-verified submissions
- **Wordle Integration**: Members can claim XP for completing daily Wordle puzzles
- **Leaderboards**: Separate leaderboards for regular members and board members
- **Auto-Enrollment**: New attendees are automatically added to the Master Roster

## Rank Thresholds

| XP Required | Rank |
|-------------|------|
| 0 | Newcomer |
| 50 | Daiyo's Classmate |
| 150 | Daiyo's Friend |
| 300 | Daiyo's Pet |
| 500 | JSA Regular |
| 750 | JSA Otaku |
| 1050 | Honorary JSA Board |

## Requirements

- Python 3.8+
- Discord Bot Token
- Google Cloud Service Account with Sheets API access
- Google Sheets for data storage

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Gamify_JSA.git
   cd Gamify_JSA
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   GOOGLE_SHEET_ID=your_google_sheet_id
   GUILD_NUM=your_discord_guild_id
   ```

4. Add your Google Cloud service account credentials as `credentials.json` in the root directory.

5. Set up your Google Sheet with the following worksheets:
   - `Master_Roster` - Columns: Name, Email, Year, Discord_ID, Total_XP, Rank, Board_Member
   - `Attendance_Logs` - Tracks processed event sheets
   - `Daily_Quests` - Quest Name, Description, Objective, Verification Method, Last_Used
   - `Weekly_Quests` - Same structure as Daily_Quests
   - `Wordle_Claims` - Tracks Wordle submissions
   - `Board_Roster` - List of board member emails

## Configuration

Edit `config.py` to customize:

- `DAILY_XP` / `WEEKLY_XP` / `WORDLE_XP` - XP rewards for different activities
- `QUEST_CHANNEL_ID` - Channel for quest announcements
- `DAILY_SUBMISSION_ID` / `WEEKLY_SUBMISSION_ID` - Channels for quest submissions
- `OFFICER_ROLE` / `OFFICER_ROLE_ID` - Role required for admin commands
- `APPROVE_EMOJI` - Emoji used by officers to approve quest submissions
- Social links (Instagram, Linktree, Calendar)

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

### Officer Commands (Require Officer Role)

| Command | Description |
|---------|-------------|
| `/process_event <sheet_url> <xp_amount>` | Process an attendance sheet and award XP |
| `/test_quest <type>` | Test a quest announcement |
| `/refresh_quest <type>` | Force a new quest announcement |
| `/post_specific_quest <type> <name>` | Post a specific quest by name |
| `/sync_board_members` | Sync board member status from Board_Roster |

## Quest System

- **Daily Quests**: Posted automatically every 24 hours
- **Weekly Quests**: Posted automatically every 7 days
- Officers approve quest submissions by reacting with ✅ in the submission channels
- Approved submissions automatically award the configured XP amount

## Project Structure

```
Gamify_JSA/
├── bot.py              # Main Discord bot with commands and event handlers
├── config.py           # Configuration and environment variables
├── requirements.txt    # Python dependencies
├── credentials.json    # Google Cloud service account credentials
├── sheets/
│   ├── client.py       # Google Sheets authentication
│   └── actions.py      # Sheet operations (XP, leaderboards, quests)
└── wordle/
    └── wordle_actions.py  # Wordle share text parsing
```

## Running the Bot

```bash
python bot.py
```

The bot will:
1. Connect to Discord and sync slash commands
2. Start the daily and weekly quest loops
3. Listen for commands and quest submission reactions

## License

This project was created for the UF Japanese Student Association.
