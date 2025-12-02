
from date_utils import start_stop_ms
from google_auth import get_gmail_service

# Email parsing
def find_text_plain(payload):
    """Recursively search for text/plain part in email payload."""
    if payload.get('mimeType') == 'text/plain':
        return payload.get('body', {}).get('data')

    if 'parts' in payload:
        for part in payload['parts']:
            result = find_text_plain(part)
            if result:
                return result

    return None

def get_message_text(service, message_id):
    """Get plain text body, timestamp, threadId, and sender from a Gmail message."""
    import base64
    msg = service.users().messages().get(userId='me', id=message_id).execute()
    sender = None
    for header in msg['payload']['headers']:
        if header['name'] == 'From': 
            sender = header['value']
    text_data = find_text_plain(msg['payload'])
    if not text_data: return None, None, None, None

    decoded = base64.urlsafe_b64decode(text_data).decode('utf-8')
    timestamp = msg['internalDate']
    threadId = msg['threadId']
    return decoded, timestamp, threadId, sender

def extract_new_content(msg_text):
    """Extract new content from email, removing quoted replies."""
    markers = ["\r\n\r\nOn ", "\r\nFrom: "]
    positions = [msg_text.find(mark) for mark in markers]
    valid_positions = [p for p in positions if p != -1]
    if valid_positions:
        split_point = min(valid_positions)
        return msg_text[:split_point]
    return msg_text

def get_thread_ids(service,label_id):
    thread_list_json = service.users().threads().list(
        userId='me',
        labelIds=[label_id]
    ).execute()
    if 'threads' not in thread_list_json: return ""
    return set([d.get('id') for d in thread_list_json['threads']])

# Note: We fetch all threads with label, then all messages in those threads, 
# then filter by date. This keeps unlabeled replies in labeled threads.
# Using q='after:X before:Y' with labelIds would miss those unlabeled messages.
# (A labled thread doesn't necessarily tag each message in the thread with the label.)
def get_messages_for_label(label_key): # → returns raw message dicts (all dates)
    service = get_gmail_service()
    label_ids=get_gmail_labels(service)
    label_id=label_ids[label_key]
    thread_ids=get_thread_ids(service,label_id)
    msg_dicts=[]
    for thread_id in thread_ids:
        thread = service.users().threads().get(userId='me', id=thread_id).execute()
        for msg in thread['messages']:
            text_data, timestamp, threadId, sender = get_message_text(service, msg['id'])
            if text_data:
                msg_dicts.append({
                    'timestamp': timestamp,
                    'threadId': threadId,
                    'sender': sender,
                    'content': extract_new_content(text_data)
                })
    return msg_dicts

def filter_by_date(msgs, date):
    start_ms, end_ms=start_stop_ms(date,1)
    return [m for m in msgs if m['timestamp'] and (start_ms <= int(m['timestamp']) < end_ms)]

def format_messages(msgs): # → does the sorting and string building
    sorted_msgs = sorted(msgs, key=lambda x: (x['threadId'], x['timestamp']))
    sub_strs = [f"From: {d['sender']}: \n\n{d['content']}\n\n=================" 
                for d in sorted_msgs]
    return '\n\n'.join(sub_strs)

def get_daily_messages(label_key, date:str):
    """Get all messages for a given label and date."""
    msg_dicts = get_messages_for_label(label_key)
    msgs = filter_by_date(msg_dicts, date)
    return format_messages(msgs)

def get_gmail_labels(service=None):
    """dict of label_id's by label name.lower()"""
    if service is None: service = get_gmail_service()
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    return {l['name'].lower(): l['id'] for l in labels if l['type']=='user'}

def label_keys(): 
    return list(get_gmail_labels())
