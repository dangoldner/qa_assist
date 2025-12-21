import os,json
from googleapiclient.discovery import build
from google.oauth2 import service_account

def get_credentials_local(scopes, token_file):
    # oauth flow (byo browswer)
    import pickle
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import Flow

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
            print("\nAfter authorizing, paste the full redirect URL here (and change to https):")
            redirect_response = input()

            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_credentials(scopes, token_file=None):
    # GitHub Actions: env var
    json_str = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    if json_str:
        info = json.loads(json_str)
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        return creds.with_subject('dan@onehealthbiosensing.com')
    # Solveit: existing pickle/OAuth flow
    return get_credentials_local(scopes,token_file)

def get_google_service(service_name, version, scopes):
    '''Authenticate and return a Google API service.'''
    token_file = f'{service_name}_token.pickle'
    creds = get_credentials(scopes,token_file)
    return build(service_name, version, credentials=creds)

def get_gmail_service():
    '''Authenticate and return Gmail API service.'''
    return get_google_service(
        'gmail', 
        'v1', 
        ['https://www.googleapis.com/auth/gmail.readonly']
    )

def get_gdocs_service():
    '''Authenticate and return GDocs API service.'''
    return get_google_service(
        'docs', 
        'v1', 
        ['https://www.googleapis.com/auth/documents']
    )

def get_gsheets_service():    
    '''Authenticate and return Google Sheets API service.'''
    return get_google_service(
        'sheets',
        'v4',
        ['https://www.googleapis.com/auth/spreadsheets']
    )
