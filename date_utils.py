
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DEF_TZ = 'US/Central'
DEF_FMT = '%Y/%m/%d' 

def ytd(tz=DEF_TZ, fmt=DEF_FMT):
    now = datetime.now(ZoneInfo(tz))
    return now-timedelta(days=1)

def str_to_date(content, year=None):
    if year is None:
        year = datetime.now().year

    formats = [
        (content,'%Y/%m/%d'),
        (content,'%Y-%m-%d'),
        (content,'%m/%d/%y'),
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

def parse_date(date,fmt=DEF_FMT,timezone=DEF_TZ):
    tz = ZoneInfo(timezone)
    return datetime.strptime(date, fmt).replace(tzinfo=tz)

def add_days(date,delta:int):
    return date+timedelta(days=delta)

def date_to_ms(date):
    return int(date.timestamp() * 1000)

def start_stop_ms(date,days,fmt=DEF_FMT,timezone=DEF_TZ):
    start_date=parse_date(date,fmt,timezone)
    end_date=add_days(start_date,days)
    return date_to_ms(start_date), date_to_ms(end_date)
