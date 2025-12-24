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
            current_xp_cell = master_sheet.cell(row_num, 5).value # Column 4 is total XP
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