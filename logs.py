
from google_auth import get_gdocs_service
from date_utils import str_to_date
from datetime import date # for type hints

def _get_paragraph_style(part):
    return (part.get('paragraph', {})
                .get('paragraphStyle', {})
                .get('namedStyleType'))

def _is_heading_level(level:int,part): 
    return _get_paragraph_style(part)==f'HEADING_{level}'

def _get_content(part):
    els = part.get('paragraph',{}).get('elements','')
    return ''.join([e.get('textRun',{}).get('content','') for e in els])

def _get_parts_list(service,doc_id):
    doc = service.documents().get(documentId=doc_id).execute()
    return doc['body']['content']

def _prepend_str(service, log_doc_id, pp_str, style='NORMAL_TEXT'):
    requests = [{
        'insertText': {
            'location': {'index': 1},
            'text': pp_str
            }
        },{
            'updateParagraphStyle': {
                'range': {'startIndex': 1, 'endIndex': len(pp_str)},
                'paragraphStyle': {'namedStyleType': style},
                'fields': 'namedStyleType'
            }
        }]
    service.documents().batchUpdate(documentId=log_doc_id, body={'requests': requests}).execute()

LOGS = {
    "assembly": "1Jb1LEU_VVorhIkslgkGOUgRADny23Z1Q310GJSo6ZWg",
    "wcp": "1S4te4jvQGokB4cSbbInO9HuQUCEY6MHRontdIplXOBo",
    "bench": "1ezsnTsRJQE8NkVId5sOqXowKopygoov9xzIl35oKczk",
    "singulation": "1C6pDV0YWWwQra3sxPSRatdNV8DjPPdeBOvzxylLIUok",
    "sterilization": "1HUfc25DiOzTIVqnFQ0FEqNqEaxs7eTosMxVKJCov9KQ",
    "algorithm": "1nxCES9tzy2ZC0aFN-B08LO5lSs4YYVsgplED0v6GXxU",
    "firmware": "1KF8LlS0UbJCdVbcqp_7BEwScJQc4EHwfI6fxNCU-SKE",
    "quality": "1uXwbWHT3PjMFg6CJCIPs8ttQYTEdE4SYqm8wmH_AIvA",
    "clinicals": "1EXJ4kd531ewCqZpD-aPqKdlMfVmRmQ9LIRsppUhSLuk",
    "submission": "1Bbr8U9iDfYPrnoFKNeMgeMxYTN6uyeTTan5cvX_WmDI"
}

def _log_to_dict_by_date(parts_list):
    log_dict = {}
    key = None
    year = None
    for part in parts_list:
        content = _get_content(part).strip()
        if _is_heading_level(2,part):
            year = int(content)
        if _is_heading_level(3,part) and content:
            key = str_to_date(content, year)
            log_dict[key] = ''
        else: 
            if key is not None: 
                log_dict[key] += content
    return log_dict

def _get_log_entries_in_range(log_dict,start_date:date,end_date:date):
    return {str(k): v for k,v in log_dict.items() #str(date) for json
            if start_date <= k <= end_date}

def _get_log_by_date(service,log_key, start_date:date, end_date:date):
    log_id = LOGS[log_key]
    parts_list = _get_parts_list(service,log_id)
    log_dict = _log_to_dict_by_date(parts_list)
    return _get_log_entries_in_range(log_dict, start_date, end_date)

def read_logs(start_date:date,end_date:date):
    "read all logs in the range"
    gdocs=get_gdocs_service()
    return {k: _get_log_by_date(gdocs,k,start_date,end_date)
            for k in list(LOGS)}

def log_keys():
    return LOGS.keys()

def write_log(key,digest,date):
    docs = get_gdocs_service()
    log_id=LOGS[key]
    _prepend_str(docs, log_id, digest + "\n", 'NORMAL_TEXT')
    _prepend_str(docs, log_id, f"{date}\n", 'HEADING_3')
