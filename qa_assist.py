def get_gmail_labels(service):
    """List all Gmail labels with their IDs."""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    return {l['name'].lower(): l['id'] for l in labels if l['type']=='user'}
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.auth import default
from googleapiclient.discovery import build
from claudette import Chat

from google.auth import iam
from google.auth.transport import requests as google_requests
from google.oauth2 import service_account

def get_google_service_keyless(service_name, version, scopes, user_email):
    """Get Google API service using service account with delegation via IAM signJwt API."""
    service_account_email = 'docs-updater@qa-assistant-458920.iam.gserviceaccount.com'
    
    # Get default credentials for signing
    signing_creds, _ = default()
    
    # Create signer that uses IAM API
    signer = iam.Signer(
        request=google_requests.Request(),
        credentials=signing_creds,
        service_account_email=service_account_email
    )
    
    # Create delegated credentials
    delegated_creds = service_account.Credentials(
        signer=signer,
        service_account_email=service_account_email,
        token_uri='https://oauth2.googleapis.com/token',
        scopes=scopes,
        subject=user_email
    )
    
    return build(service_name, version, credentials=delegated_creds)

def get_gmail_service_keyless():
    return get_google_service_keyless(
        'gmail', 
        'v1', 
        ['https://www.googleapis.com/auth/gmail.readonly'],
        'dan@onehealthbiosensing.com'
    )

def get_gdocs_service_keyless():
    return get_google_service_keyless(
        'docs', 
        'v1', 
        ['https://www.googleapis.com/auth/documents'],
        'dan@onehealthbiosensing.com'
    )
    
def get_gsheets_service_keyless():
    return get_google_service_keyless(
        'sheets', 
        'v4', 
        ['https://www.googleapis.com/auth/spreadsheets'],
        'dan@onehealthbiosensing.com'
    )

# Cloud Function entry point
def update_logs_daily(request):
    """Cloud Function entry point - runs on schedule."""
    gmail = get_gmail_service_keyless()
    docs = get_gdocs_service_keyless()
    cleaner = get_email_cleaner()
    
    update_logs(gmail, docs, cleaner)
    
    return 'Logs updated successfully'
def update(qdoc,logs):
    props = get_props(logs,qdoc)
    news = filter_props(props,qdoc)
    if news: qdoc.add_entries(news)

def update_all_docs(start_date,end_date):
    logs=get_logs(start_date,end_date)
    if not any(logs.values()): return
    for qdoc in [rreg,dlog,dio]: 
        update(qdoc,logs)
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def update_qdocs_weekly(request):
    "To be run Friday mornings at 4am for the previous week (Fr-Th)"
    now = datetime.now(ZoneInfo('US/Central'))
    end_date = (now - timedelta(hours=6)).date() #from 4h ago, with a margin
    start_date = end_date - timedelta(days=7)
    update_all_docs(start_date,end_date)
    return f"Quality docs updated through {end_date.strftime('%d/%m/%Y')}"