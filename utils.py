
from datetime import date
def ytd(tz='US/Central',fmt='%Y/%m/%d'):
    return (datetime.now(ZoneInfo(tz_str)) - timedelta(days=1)).strftime(fmt)
