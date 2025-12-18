from sheets.client import get_client
import config 

client = get_client()
sheet = client.open_by_key(config.SHEET_ID)

# Access tabs.
master_roster = sheet.worksheet("Master_Roster")
attendance_logs = sheet.worksheet("Attendance_Logs")

# Should print "Arisa is a bozo"
print(sheet.worksheet("Master_Roster").row_values(1))
