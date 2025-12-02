
# CLOUD DEPLOYMENT: When creating main.py, combine all modules but replace google_auth functions
# with the keyless versions below. 

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.auth import default, iam
from google.auth.transport import requests as google_requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT = 'docs-updater@qa-assistant-458920.iam.gserviceaccount.com'
USER_EMAIL = 'dan@onehealthbiosensing.com'

def get_google_service(service_name, version, scopes, user_email=USER_EMAIL):
    """Get Google API service using service account with delegation via IAM signJwt API."""
    signing_creds, _ = default()
    signer = iam.Signer(
        request=google_requests.Request(),
        credentials=signing_creds,
        service_account_email=SERVICE_ACCOUNT
    )
    delegated_creds = service_account.Credentials(
        signer=signer,
        service_account_email=SERVICE_ACCOUNT,
        token_uri='https://oauth2.googleapis.com/token',
        scopes=scopes,
        subject=user_email
    )
    return build(service_name, version, credentials=delegated_creds)

def get_gmail_service():
    return get_google_service('gmail', 'v1', 
        ['https://www.googleapis.com/auth/gmail.readonly'])

def get_gdocs_service():
    return get_google_service('docs', 'v1', 
        ['https://www.googleapis.com/auth/documents'])

def get_gsheets_service():
    return get_google_service('sheets', 'v4', 
        ['https://www.googleapis.com/auth/spreadsheets'])

# Cloud Function entry points

def update_logs_daily(request):
    """Cloud Function entry point - updates logs from yesterday's emails."""
    from core import update_logs
    update_logs()
    return 'Logs updated successfully'

def update_qdocs_weekly(request):
    """Cloud Function entry point - run Fridays at 4am for prior week (Fr-Th)."""
    from core import update_qdocs
    now = datetime.now(ZoneInfo('US/Central'))
    end_date = (now - timedelta(hours=6)).date()
    start_date = end_date - timedelta(days=7)
    update_qdocs(start_date, end_date)
    return f"Quality docs updated through {end_date.strftime('%Y/%m/%d')}"
