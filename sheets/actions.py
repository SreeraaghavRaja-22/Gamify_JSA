import re # searches text patterns python-regular expression module
import gspread 

# --- RANK CONFIGURATION ---
# Centralized place to change rank names and their XP requirements.
RANK_THRESHOLDS = {
    0: "Newcomer",
    100: "Rank 1",
    200: "Rank 2",
    300: "Rank 3",
    400: "Rank 4",
    500: "Rank 5"
}

# --- HEADER CONFIGURATION ---
# Define the exact headers in your Master_Roster to fix the "duplicate headers" error.
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

def process_event_data(client, master_sheet_id, event_sheet_url, xp_amount):
    # Opens Event Sheet -> Opens Master Roster -> 
    # Awards XP to exising members -> Auto-enrolls new members

    # 1. Opens the Event Sheet (the new form)
    event_id = get_id_from_url(event_sheet_url)
    if not event_id: 
        return "❌Error: Could not parse Sheet ID From that URL."
    
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
    
    # 4. Creates a lookup directory for Master Roster for speed
    # Format: {'email@ufl.edu': Row_Number}
    # gspread is 1-indexed, and row 1 is headers. So data starts at row 2
    master_map = {}
    for i, row in enumerate(master_records):
        # i starts at 0, represent row 2 (data) - actual row is i + 2
        email = str(row.get("Email", "")).strip().lower()
        if email: 
            master_map[email] = i + 2

    new_members_count = 0
    existing_members_count = 0

    # 5. Loop through Event Attendees
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

    return f"✅ Success! Updated {existing_members_count} and added {new_members_count}"

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
            return "This Discord Account is already registered."

        if row.get("Email", "").strip().lower() == email:
            
            # Case 2: Email is in Master Roster but is not linked to a Discord account.
            if row_discord_id == "":
                row_number = i + 2
                master.update_cell(row_number, 4, discord_id)
                return "Your Discord account has been linked."
            
            # Case 3: Email is linked to another Discord account.
            return "This email is already linked to another Discord account."

    # Case 4: Email is not in Master Roster. 
    new_row = [
        "", # Name
        email, # Email
        "", # Year
        discord_id, # Discord ID
        0, # Total XP
        "Newcomer" # Tier
    ]
    master.append_row(new_row)
    return "You have been registered successfully on JSA's XP system."

def get_leaderboard(client, master_sheet_id, top=10, include_board_members=False):
    sheet = client.open_by_key(master_sheet_id)
    master = sheet.worksheet("Master_Roster")
    records = master.get_all_records()

    leaderboard_data = []
    for row in records:
        # .strip() is crucial: Discord won't bold if there is a space inside the **
        name = str(row.get("Name", "Unknown")).strip()
        xp_val = row.get("Total_XP", 0)
        rank_name = str(row.get("Rank", "Unknown")).strip()
        board_member = str(row.get("Board_Member", "N")).strip().upper()

        if not include_board_members and board_member == "Y":
            continue
        
        try:
            xp = int(xp_val)
        except:
            xp = 0
        leaderboard_data.append((name, xp, rank_name))

    leaderboard_data.sort(key=lambda x: x[1], reverse=True)

    # Using Hangul Filler (\u3164) for alignment - it is more stable than Braille dots
    s = "\u3164" 

    # Header - Wrap the bolding tightly around the text
    message = f"╭━━━ {s*2} ⚔️ **JSA LEADERBOARD** ⚔️ {s*2} ━━━╮\n\n"
    
    last_xp = None
    shown = 0

    for index, (name, xp, rank_name) in enumerate(leaderboard_data):
        if xp != last_xp:
            place = index + 1
            last_xp = xp

        medal = "🥇" if place == 1 else "🥈" if place == 2 else "🥉" if place == 3 else "⭐"
        suffix = "st" if place == 1 else "nd" if place == 2 else "rd" if place == 3 else ")"
        
        # We now bold the ENTIRE line including the medal. 
        # This is the most reliable way to force Discord to render the bolding.
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
                # Limit to 20 people to prevent the message from failing to bold/send
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
