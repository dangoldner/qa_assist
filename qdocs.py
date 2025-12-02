
from google_auth import get_gsheets_service

class GSheet:
    "A google sheet"
    def __init__(self,sheet_id:str,tab_range:str):
        self.sheet_id=sheet_id # gsheet document id
        self.tab_range=tab_range #gsheet tab & range

    def get_rows(self):
        gsheets=get_gsheets_service()
        result = gsheets.spreadsheets().values().get(
            spreadsheetId=self.sheet_id,
            range=self.tab_range
        ).execute()
        return result.get('values',[])

    def append(self,rows):
        gsheets=get_gsheets_service()
        gsheets.spreadsheets().values().append(
            spreadsheetId=self.sheet_id,
            range=self.tab_range,  
            valueInputOption='RAW',  # or 'USER_ENTERED'
            body={'values': rows}
        ).execute()

class QDoc(GSheet):
    "Quality Document (Risk Register, Decision Log, Design I/O Matrix)"
    def __init__(self, sheet_id, tab_range, entry_f):
        super().__init__(sheet_id, tab_range)
        self.entry_f = entry_f #doc entry defn function
        self.rows = self.get_rows()
        self._headers = self.rows[0] if self.rows else []

    @staticmethod
    def _sort_by_date_if_present(prop_dicts):
        if not prop_dicts or 'Date' not in prop_dicts[0]: return prop_dicts
        return sorted(prop_dicts, key=lambda d: d.get('Date', ''))

    def _mk_row(self,prop):
        return [prop.get(h,'') for h in self._headers]

    def add_entries(self,props):
        props=self._sort_by_date_if_present(props)
        rows=[self._mk_row(prop) for prop in props]
        self.append(rows)

def qdocs(): 
    def risk_f(hazard:str, harms:str, causes:str)->dict:
        "Candidate Risk Register entry"
        return {'Hazard': hazard,
            'Potential Harms': harms,
            'Possible Causes': causes,
            'Reviewed': 'FALSE'}

    def decision_f(component:str,decision:str,rationale:str,date:str)->dict:
        "Candidate Decision Log entry"
        return {'Component': component,
            'Decision': decision,
            'Rationale': rationale,
            'Date': date,
            'Reviewed': 'FALSE'}

    def design_f(design_input:str,source_rationale:str,design_output:str,verif_valid_method:str)->dict:
        "Candidate Design Input/Output Matrix entry"
        return {'Design Input': design_input,
            'Source / Rationale': source_rationale,
            'Design Output': design_output,
            'Verification/Validation Method': verif_valid_method,
            'Reviewed': 'FALSE'}

    rreg = QDoc(
        sheet_id='1j752K9N89Qv9WLkjje3OWkrzDbSMjLwYuxdoTfArcpQ',
        tab_range='Risk Register!A:L',
        entry_f=risk_f)
    dlog = QDoc(
        sheet_id='14oGD5hwGP_8OLfq_tqQVdEjicRzJ4cyQWPkXz92avv4',
        tab_range='Decision Log!A:G',
        entry_f=decision_f)   
    dio = QDoc(
        sheet_id='1xrV_39iaVoTpAXmbxbKfFBBnbdHN5yeyKJMDZ59MdqM',
        tab_range='Design IO Matrix!A:G',
        entry_f=design_f)
    return [rreg,dlog,dio]

