import re # searches text patterns python-regular expression module
import gspread 

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
        master_records = master_sheet.get_all_records()
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
            master_sheet.update_cell(row_num, 5, new_xp)
            master_sheet.update_cell(row_num, 6, "Regular")
            existing_members_count += 1
            print(f"Updated {attendee_email}: {current_xp} -> {new_xp}")

        else:
            # Scenario B: The Newcomer (Auto-Enroll)
            new_row = [attendee_name, attendee_email, attendee_year, "", xp_amount, "Newcomer"]
            master_sheet.append_row(new_row)
            new_members_count += 1
            print(f"Added {attendee_email}!")

    return f"✅Success! Updated {existing_members_count} and added {new_members_count}"

def get_join(client, master_sheet_id, email, discord_id):
    sheet = client.open_by_key(master_sheet_id)
    master = sheet.worksheet("Master_Roster")
    email = email.strip().lower()
    discord_id = str(discord_id).strip()

    records = master.get_all_records()
    for i, row in enumerate(records):
        row_discord_id = str(row.get("Discord_ID", "")).strip()
        row_email = str(row.get("Email", "")).strip().lower()

        # If this row matches the email
        if row_email == email:
            # If Discord ID is empty, Link it
            if row_discord_id == "":
                row_number = i + 2
                master.update_cell(row_number, 4, discord_id)
                return f"✅ Success! Linked {email} to this Discord account."
            
            # If Discord ID is ALREADY this user
            if row_discord_id == discord_id:
                return "ℹ️ You are already linked to this email."
            
            # If Discord ID belongs to someone else
            return "❌ This email is already linked to a different Discord account."

    # If email not found in sheet
    # Create new user
    new_row = ["", email, "", discord_id, 0, "Newcomer"]
    master.append_row(new_row)
    return f"✅ Registered new account for {email}!"

def get_leaderboard(client, master_sheet_id, top=10, include_board_members=False):
    sheet = client.open_by_key(master_sheet_id)
    master = sheet.worksheet("Master_Roster")
    records = master.get_all_records()

    leaderboard_data = []
    
    for row in records:
        name = row.get("Name", "Unknown")
        try: xp = int(row.get("Total_XP", 0))
        except: xp = 0
        
        # Filter out empty names or 0 XP if you want
        if name and xp >= 0:
            leaderboard_data.append((name, xp))

    # Sort by XP (Highest first)
    leaderboard_data.sort(key=lambda x: x[1], reverse=True)

    message = "**🏆 JSA Leaderboard 🏆**\n"
    count = 0
    for i, (name, xp) in enumerate(leaderboard_data):
        if count >= top: break
        
        rank_emoji = "🔹"
        if i == 0: rank_emoji = "🥇"
        elif i == 1: rank_emoji = "🥈"
        elif i == 2: rank_emoji = "🥉"

        message += f"{rank_emoji} **{name}**: {xp} XP\n"
        count += 1
        
    return message

def get_xp(client, master_sheet_id, discord_id):
    discord_id = str(discord_id).strip()
    sheet = client.open_by_key(master_sheet_id)
    master = sheet.worksheet("Master_Roster")

    records = master.get_all_records()
    for row in records:
        if str(row.get("Discord_ID", "")).strip() == discord_id:
            try: xp = int(row.get("Total_XP", 0))
            except: xp = 0
            
            return f"✨ You currently have **{xp} XP**!"
        
    return "❌ You aren't registered yet! Use `!join [email]` first."