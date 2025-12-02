
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

def get_google_service(service_name, version, scopes, token_file):
    '''Authenticate and return a Google API service.'''
    creds = None

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "web": {
                    "client_id": os.environ.get('QA_ASST_CLIENT_ID'),
                    "client_secret": os.environ.get('QA_ASST_CLIENT_SECRET'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8080"]
                }
            }

            flow = Flow.from_client_config(
                client_config, 
                scopes=scopes
            )
            flow.redirect_uri = 'http://localhost:8080'

            auth_url, state = flow.authorization_url(
                access_type='offline',
                prompt='consent'
            )

            print("Visit this URL to authorize:")
            print(auth_url)
            print("\nAfter authorizing, paste the full redirect URL here:")
            redirect_response = input()

            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return build(service_name, version, credentials=creds)

def get_gmail_service():
    '''Authenticate and return Gmail API service.'''
    return get_google_service(
        'gmail', 
        'v1', 
        ['https://www.googleapis.com/auth/gmail.readonly'],
        'gmail_token.pickle'
    )

def get_gdocs_service():
    '''Authenticate and return GDocs API service.'''
    return get_google_service(
        'docs', 
        'v1', 
        ['https://www.googleapis.com/auth/documents'],
        'docs_token.pickle'
    )

def get_gsheets_service():    
    '''Authenticate and return Google Sheets API service.'''
    return get_google_service(
        'sheets',
        'v4',
        ['https://www.googleapis.com/auth/spreadsheets'],
        'sheets_token.pickle'
    )
