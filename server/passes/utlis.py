from datetime import date, datetime
from passes.models import LunchTiming, Logging
from typing import Dict
import pytz


def roll_to_year(rno):
    today = datetime.today()
    year = today.year - int(f"20{rno[0:2]}")
    if today.month >= 9:
        year += 1
    return year


def get_timings(today: datetime, year: int) -> Dict[str, datetime]:
    timings = LunchTiming.objects.get(year=year)
    opening_arr = timings.opening_time.split(":")
    closing_arr = timings.closing_time.split(":")
    opening_time = today.replace(
        hour=int(opening_arr[0]), minute=int(opening_arr[1]), second=0, microsecond=0
    )
    closing_time = today.replace(
        hour=int(closing_arr[0]), minute=int(closing_arr[1]), second=0, microsecond=0
    )

    return {"open": opening_time, "close": closing_time}


def get_local_date(timestamp: int):
    resDate = ""
    try:
        date = datetime.fromtimestamp(timestamp).astimezone(pytz.timezone("Asia/Kolkata"))
        resDate = date.strftime("%d-%m-%Y %H:%M")
    except ValueError:
        date = datetime.fromtimestamp(timestamp/int(10e6)).astimezone(pytz.timezone("Asia/Kolkata"))
        resDate = date.strftime("%d-%m-%Y %H:%M")
    return resDate


def log(roll_no: str) -> int | None:
    # print(datetime.fromtimestamp(datetime.today().timestamp()))
    last_logged = Logging.objects.filter(roll_no=roll_no).last()
    try:
        Logging.objects.create(time=datetime.today().timestamp(), roll_no=roll_no)
        if not last_logged:
            return None
        else:
            return last_logged.time
    except:
        return -1
