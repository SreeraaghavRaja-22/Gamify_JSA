import re 
import gspread 
import random
from datetime import datetime

# --- RANK CONFIGURATION ---
RANK_THRESHOLDS = {
    0: "Newcomer",
    50: "Daiyo's Classmate",
    150: "Daiyo's Friend",
    300: "Daiyo's Pet",
    500: "JSA Regular",
    750: "JSA Otaku",
    1050: "Honorary JSA Board"
}

# --- HEADER CONFIGURATION ---
MASTER_HEADERS = ['Name', 'Email', 'Year', 'Discord_ID', 'Total_XP', 'Rank']

def calculate_rank(xp):
    # Calculates the rank name based on XP thresholds.
    sorted_thresholds = sorted(RANK_THRESHOLDS.keys(), reverse=True)
    for threshold in sorted_thresholds:
        if xp >= threshold:
            return RANK_THRESHOLDS[threshold]
    return "Newcomer"

def get_id_from_url(url):
    # Extracts the long alphanumeric ID from a Google Sheet URL 
    try:
        # Regex to find the ID between /d/ and / 
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if match: 
            return match.group(1)
        else:
            return None
    except:
        return None
    
def find_email_column(records):
    # Scans the first row of data to find which key looks like an email 
    if not records: 
        return None
    
    # Gets the keys (headers) from the first row
    headers = records[0].keys()

    for header in headers:
        clean_header = header.lower().strip()
        # Looks for email, uf email, email address
        if "email" in clean_header:
            return header
    return None

def is_event_processed(log_sheet, event_id):
    # Checks if the event_id already exists in Column A of Attendance_Logs
    try:
        # Get all IDs from the first column
        processed_ids = log_sheet.col_values(1) 
        return event_id in processed_ids
    except:
        return False
    
def log_event_completion(log_sheet, event_id, xp_amount):
    # Writes the receipt to Attendance_Logs so we don't process it again 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_sheet.append_row([event_id, timestamp, xp_amount])

def process_event_data(client, master_sheet_id, event_sheet_url, xp_amount):
    # Opens Event Sheet -> Opens Master Roster -> 
    # Awards XP to exising members -> Auto-enrolls new members

    # 1. Gets the Event ID
    event_id = get_id_from_url(event_sheet_url)
    if not event_id: 
        return "❌Error: Could not parse Sheet ID From that URL."
    
    # 2. Opens the Master Roster & Attendance Log
    try: 
        master_wb = client.open_by_key(master_sheet_id)
        master_sheet = master_wb.worksheet("Master_Roster")
        log_sheet = master_wb.worksheet("Attendance_Logs")
    except Exception as e: 
        return f"❌Error opening Master Roster: {e}"
    
    # 3. Checks if Event Sheet has been processed
    if is_event_processed(log_sheet, event_id):
        return "⚠️ STOP: This event sheet has already been processed! Check 'Attendance_Logs' for details."

    # 4. Opens the Event Sheet
    try: 
        event_sheet = client.open_by_key(event_id).sheet1
        event_records = event_sheet.get_all_records()
    except Exception as e: 
        return f"❌Error opening Event Sheet: {e}"
    
    # 2. Opens the Master Roster
    try: 
        master_wb = client.open_by_key(master_sheet_id)
        master_sheet = master_wb.worksheet("Master_Roster")
        master_records = master_sheet.get_all_records(expected_headers=MASTER_HEADERS)
    except Exception as e: 
        return f"❌Error opening Master Roster: {e}"

    # 3. Finds the Email Column in the Event Sheet
    email_col_name = find_email_column(event_records)
    if not email_col_name: 
        return "❌Error: Could not find a column name 'Email' in the event sheet. "
    
    # 6. Creates a lookup directory for Master Roster for speed
    # Format: {'email@ufl.edu': Row_Number}
    # gspread is 1-indexed, and row 1 is headers. So data starts at row 2
    master_records = master_sheet.get_all_records()
    master_map = {}
    for i, row in enumerate(master_records):
        # i starts at 0, represent row 2 (data) - actual row is i + 2
        email = str(row.get("Email", "")).strip().lower()
        if email: 
            master_map[email] = i + 2

    new_members_count = 0
    existing_members_count = 0

    # 7. Process Attendees
    for row in event_records:
        attendee_email = str(row[email_col_name]).strip().lower()
        attendee_name = row.get("Name (First & Last)", "Unknown") # Fallback if Name column missing 
        attendee_year = row.get("Year", "")

        # If email is empty, skip
        if not attendee_email:
            continue

        if attendee_email in master_map: 
            # Scenario A: The Regular (Update XP)
            row_num = master_map[attendee_email]

            # Get current XP (handle empty cells)
            current_xp_cell = master_sheet.cell(row_num, 5).value # Column 5 is total XP
            try: 
                current_xp = int(current_xp_cell)
            except: 
                current_xp = 0

            new_xp = current_xp + xp_amount
            new_rank = calculate_rank(xp_amount)

            master_sheet.update_cell(row_num, 5, new_xp)
            master_sheet.update_cell(row_num, 6, new_rank)
            existing_members_count += 1
            print(f"Updated {attendee_email}: {current_xp} -> {new_xp}")

        else:
            # Scenario B: The Newcomer (Auto-Enroll)
            new_row = [attendee_name, attendee_email, attendee_year, "", xp_amount, "Newcomer"]
            master_sheet.append_row(new_row)
            new_members_count += 1
            print(f"Added {attendee_email}!")

    # 8. Log the transaction so it doesn't happen again
    log_event_completion(log_sheet, event_id, xp_amount)

    return f"✅  Success! Processed Sheet ID {event_id[:5]}... Updated {existing_members_count} and added {new_members_count}."

def get_join(client, master_sheet_id, email, discord_id):
    sheet = client.open_by_key(master_sheet_id)
    master = sheet.worksheet("Master_Roster")
    email = email.strip().lower()
    discord_id = str(discord_id).strip()

    records = master.get_all_records()
    for i, row in enumerate(records):

        row_discord_id = str(row.get("Discord_ID", "")).strip()
        
        # Case 1: Email and Discord account are already linked.
        if row_discord_id == discord_id:
            return "✨ **You're already in!** This Discord account is already registered in our system."

        if row.get("Email", "").strip().lower() == email:
            
            # Case 2: Email is in Master Roster but is not linked to a Discord account.
            if row_discord_id == "":
                row_number = i + 2
                master.update_cell(row_number, 4, discord_id)
                return "🔗 **Account Linked!** We've successfully connected your Discord to your JSA records. Welcome!"
            
            # Case 3: Email is linked to another Discord account.
            return "⚠️ **Oops!** That email is already connected to a different Discord account."

    # Case 4: Email is not in Master Roster. 
    new_row = [
        "", # Name
        email, # Email
        "", # Year
        discord_id, # Discord ID
        0, # Total XP
        "Newcomer" # Rank
    ]
    master.append_row(new_row)
    return "🎉 **Welcome aboard!** You've been successfully registered in the JSA XP system. Time to start earning! 🚀"

def get_leaderboard(client, master_sheet_id, top=10, mode="regular"):
    sheet = client.open_by_key(master_sheet_id)
    master = sheet.worksheet("Master_Roster")
    records = master.get_all_records()

    leaderboard_data = []
    for row in records:
        name = str(row.get("Name", "Unknown")).strip()
        xp_val = row.get("Total_XP", 0)
        rank_name = str(row.get("Rank", "Unknown")).strip()
        is_board = str(row.get("Board_Member", "N")).strip().upper() == "Y"

        # Filtering Logic
        if mode == "regular" and is_board:
            continue
        if mode == "board" and not is_board:
            continue
        
        try:
            xp = int(xp_val)
        except:
            xp = 0
        leaderboard_data.append((name, xp, rank_name))

    leaderboard_data.sort(key=lambda x: x[1], reverse=True)

    # Using Hangul Filler (\u3164) for alignment 
    s = "\u3164" 

    # Header
    message = f"╭━━━ {s*2} ⚔️ **JSA LEADERBOARD** ⚔️ {s*2} ━━━╮\n\n"
    
    last_xp = None
    shown = 0

    for index, (name, xp, rank_name) in enumerate(leaderboard_data):
        if xp != last_xp:
            place = index + 1
            last_xp = xp

        medal = "🥇" if place == 1 else "🥈" if place == 2 else "🥉" if place == 3 else "⭐"
        suffix = "st" if place == 1 else "nd" if place == 2 else "rd" if place == 3 else ")"
        
        if place <= 3:
            message += f"{s*6} {medal} {place}{suffix} | {name}\n"
            message += f"{s*8} ★ {xp} XP ★\n"
            message += f"{s*8} {rank_name} (ง•̀o•́)ง \n\n"
        else:
            message += f"{s*4} {medal} {place}) {name} ★ {xp} XP ★\n"
        
        shown += 1

        # WARNING: If too many people have the same XP, the message will break 2000 characters.
        if shown >= top:
            if index + 1 < len(leaderboard_data) and leaderboard_data[index + 1][1] == xp:
                # Limits to 20 people to prevent the message from failing 
                if shown > 20: 
                    message += f"{s*3} ... and more tied with {xp} XP ...\n"
                    break
                continue
            break

    message += f"\n╰━━━━━━ {s*6} 🏯 {s*6} ━━━━━━╯"

    return message

def get_xp(client, master_sheet_id, discord_id):
    discord_id = str(discord_id).strip()
    sheet = client.open_by_key(master_sheet_id)
    master = sheet.worksheet("Master_Roster")

    records = master.get_all_records()
    for row in records:
        row_discord_id = str(row.get("Discord_ID", "")).strip()
        if row_discord_id == discord_id:
            try:
                xp = int(row.get("Total_XP", 0))
            except:
                xp = 0
            
            rank = row.get("Rank", "Unknown")
            return (f"Your rank is \"{rank}\" and you currently have {xp} XP!")
        
    return "Your Discord account was not found in JSA's XP system.\nPlease register using the join command (Ex: !join email@ufl.edu)."

def award_quest_xp(client, master_sheet_id, discord_id, xp_amount):
    # Finds a user by Discord ID and adds XP to Master Roster
    try: 
        sheet = client.open_by_key(master_sheet_id)
        master = sheet.worksheet("Master_Roster")
        records = master.get_all_records(expected_headers=MASTER_HEADERS)
    except Exception as e:
        return f"❌ Error accessing Sheet: {e}"
    
    for i, row in enumerate(records):
        # Finds the row matching the user's Discord ID
        if str(row.get("Discord_ID", "")).strip() == str(discord_id):
            row_num = i + 2 # Accounts for header and 1-indexing
            
            # Calculates new XP
            try:
                current_xp = int(row.get("Total_XP", 0))
            except:
                current_xp = 0
            
            new_xp = current_xp + xp_amount
            new_rank = calculate_rank(new_xp)

            # Updates XP and Rank
            master.update_cell(row_num, 5, new_xp)
            master.update_cell(row_num, 6, new_rank)

            return f"Added {xp_amount} XP! New Total: {new_xp} ({new_rank})"
            
    return "❌ User not found in roster. Please use !join first."

def get_random_quest(client, master_sheet_id, sheet_name):
    # Picks a random quest from the specified sheet and avoids back-to-back repeats
    try:
        spreadsheet = client.open_by_key(master_sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        records = worksheet.get_all_records()
        headers = worksheet.row_values(1)
        
        # Ensure the 'Last_Used' column exists in your sheet headers
        if "Last_Used" not in headers:
            return None
        last_used_col_idx = headers.index("Last_Used") + 1

        if not records:
            return None

        # Sort quests by Last_Used timestamp (most recent first)
        # We add the original row index (i+2) to each record for updating later
        indexed_records = []
        for i, r in enumerate(records):
            indexed_records.append({"data": r, "row_num": i + 2})

        indexed_records.sort(key=lambda x: str(x["data"].get("Last_Used", "")), reverse=True)

        # Exclude the most recently used quest if there is more than one
        pool = indexed_records[1:] if len(indexed_records) > 1 else indexed_records
        selection = random.choice(pool)

        # Update the timestamp in the sheet
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.update_cell(selection["row_num"], last_used_col_idx, now_str)

        return selection["data"]
    except Exception as e:
        print(f"Error fetching quest from {sheet_name}: {e}")
        return None

def get_specific_quest(client, master_sheet_id, sheet_name, quest_name):
    # Fetches a specific quest by its name from the sheet
    try:
        spreadsheet = client.open_by_key(master_sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        records = worksheet.get_all_records()
        headers = worksheet.row_values(1)
        
        if "Last_Used" not in headers:
            return None
        last_used_col_idx = headers.index("Last_Used") + 1

        # Searches for the quest by name
        for i, row in enumerate(records):
            if str(row.get("Quest Name", "")).strip().lower() == quest_name.strip().lower():
                # Updates the timestamp 
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                worksheet.update_cell(i + 2, last_used_col_idx, now_str)
                return row
        return None
    except Exception as e:
        print(f"Error fetching specific quest: {e}")
        return None

# wordle_claim_exists (function to return if the wordle is already claimed 
def wordle_claim_exists(client, master_sheet_id, puzzle, discord_id):
    sheet = client.open_by_key(master_sheet_id)
    wordle_sheet = sheet.worksheet("Wordle_Claims")

    # converts the puzzle and discord_id to strings
    puzzle = str(puzzle).strip()
    discord_id = str(discord_id).strip()

    # loop through each row and see if the puzzle has already been claimed by a corresponding discord id 
    rows = wordle_sheet.get_all_values()
    for row in rows[1:]:
        if len(row) >= 2 and row[0].strip() == puzzle and row[1].strip() == discord_id:
            return True
    return False

# log the wordle claim 
def log_wordle_claim(client, master_sheet_id, puzzle, discord_id):
    sheet = client.open_by_key(master_sheet_id)
    wordle_sheet = sheet.worksheet("Wordle_Claims")

    # logs the wordle claim 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    wordle_sheet.append_row([str(puzzle), str(discord_id), timestamp], value_input_option = "RAW")

# compares the two sheets and checks if the member is a board member, if so, add y/n to board member column
def check_if_board_member(client, master_sheet_id):
    sheet = client.open_by_key(master_sheet_id)
    master = sheet.worksheet("Master_Roster")
    board_members = sheet.worksheet("Board_Roster")

    # 1. Retrieve all data from master sheet and board members sheet
    master_records = master.get_all_records()
    board_records = board_members.get_all_records()

    # 2. Build a lookup set of board member emails
    board_emails = {
        row["Email"].strip().lower()
        for row in board_records
        if row.get("Email")
    }

    # 3. Find the column inded for board_member
    headers = master.row_values(1)
    board_col = headers.index("Board_Member") + 1
    email_col = headers.index("Email") + 1

    updates = []

    # 4. Decide Y/N for each row
    for i, row in enumerate(master_records, start=2):
        email = row.get("Email", "").strip().lower()

        is_board = "Y" if email in board_emails else "N"

        # need to ascii align to get capital letters (get values like D1, D2...DX)
        updates.append({
            "range": f"{chr(64 + board_col)}{i}",
            "values": [[is_board]]
        })

    # 5. Batch update for efficiency
    master.batch_update(updates)
