
from claudette import Chat, Client
from date_utils import ytd
from emails import label_keys, get_daily_messages
from logs import log_keys, write_log, read_logs
from qdocs import qdocs

# update logs

def get_email_cleaner():
    instr = """Please format this as a clean plain-text chronological transcript by:
    1. Removing all email signature blocks
    2. Removing any quoted/forwarded text
    3. For each message: sender's name, colon, then the message body
    4. After each message: "---" with no newlines or returns (no blank lines)
    5. Keep it tight - no additional blank lines
    6. Plain text only - no markdown formatting"""
    return Chat(model='claude-sonnet-4-20250514', sp=instr)

def clean(messages):
    c = get_email_cleaner()
    r = c(messages)
    return r.content

def update_logs(date=None):
    """update all logs based on emails from date (default yesterday)"""
    if date is None: date=ytd()
    for k in (set(label_keys()) & set(log_keys())): 
        messages = get_daily_messages(k, date)
        if not messages: return
        clean_digest = clean(messages)
        if not clean_digest: return
        write_log(k,clean_digest,date)

## Update quality docs 

def _entries_prompt(logs):
    p = f"""Review this set of engineering logs from a continuous glucose monitor development project
            and identify candidate entries to the quality document represented in the tool. Focus on items 
            of significant, long-term importance; ignore short-term operational or execution issues. Keep 
            each field terse (10-20 words max).

            Logs:
            {logs} 
        """
    return p

def _get_props(logs, qdoc):
    """propose entries for qdoc before seeing existing entries"""
    c = Client('claude-sonnet-4-5')
    return c.structured(_entries_prompt(logs),[qdoc.entry_f])

def _filter_props(props, qdoc):
    p = f"""
    Determine which proposed new entries are NOT already documented the given existing document. 
    Return ONLY those proposals that represent genuinely NEW concepts not already captured in existing entries. 
    - Ignore wording differences - focus on whether the core concept is already documented.
    - If a proposal is semantically similar to an existing entry, exclude it.
    - If NONE of the proposals are new, make NO tool calls.

    Proposals:
    {props}

    Existing entries:
    {qdoc.rows}
    """
    c = Client('claude-sonnet-4-5')
    return c.structured(p,qdoc.entry_f)

def update_qdocs(start_date,end_date):
    entries=read_logs(start_date,end_date)
    if not any(entries.values()): return
    for qdoc in qdocs(): 
        props = _get_props(entries,qdoc)
        news = _filter_props(props,qdoc)
        if news: qdoc.add_entries(news)

