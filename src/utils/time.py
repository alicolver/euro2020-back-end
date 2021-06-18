import pytz
from datetime import datetime


def now():
    timezone = pytz.timezone('Europe/London')
    now = datetime.now(timezone)
    return now
