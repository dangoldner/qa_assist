
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DEF_TZ = 'US/Central'
DEF_FMT = '%Y/%m/%d' 

def today(tz=DEF_TZ):
    return datetime.now(ZoneInfo(tz)).date()

def add_days(n:int,date=None,tz=DEF_TZ):
    date = date or today(tz)
    return date+timedelta(days=n)

def make_day_offset(n):
    def offset(date=None, tz=DEF_TZ):
        return add_days(n, date, tz)
    return offset

ytd = make_day_offset(-1)
wk_ago = make_day_offset(-7)

def str_to_date(content, year=None):
    if year is None:
        year = datetime.now().year

    formats = [
        (content,'%Y/%m/%d'),
        (content,'%Y-%m-%d'),
        (content,'%m/%d/%y'),
        (content,'%m/%d/%Y'),
        (f'{year}/{content}','%Y/%m/%d'),
        (f'{content} {year}', '%d %b %Y'),
        (f'{content} {year}', '%d %B %Y'),
        (f'{content} {year}', '%b %d %Y'),
        (f'{content} {year}', '%B %d %Y')
    ]

    for fmt in formats:
        try:
            return datetime.strptime(fmt[0], fmt[1]).date()
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {content}")

def date_to_ms(date):
    return int(date.timestamp() * 1000)

def start_stop_ms(start_date,days):
    end_date=add_days(days,start_date)
    return date_to_ms(start_date), date_to_ms(end_date)
