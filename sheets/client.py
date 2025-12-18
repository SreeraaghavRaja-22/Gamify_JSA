import gspread
from google.oauth2.service_account import Credentials

# Allow R/W operations in google sheets
# Allow accessing files in GDrive.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    # Authorize and return a gspread client
    creds = Credentials.from_service_account_file(
        "credentials.json", 
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client