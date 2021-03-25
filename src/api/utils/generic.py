"""Util Generic."""
# Standard Python Libraries
from datetime import datetime, timedelta
import math

# Third-Party Libraries
import dateutil.parser
from django.utils import timezone
import pytz


def current_season():
    """Get Current Season."""
    today = datetime.today()
    Y = today.year
    seasons = [
        ("winter", (datetime(Y, 1, 1), datetime(Y, 3, 20))),
        ("spring", (datetime(Y, 3, 21), datetime(Y, 6, 20))),
        ("summer", (datetime(Y, 6, 21), datetime(Y, 9, 22))),
        ("autumn", (datetime(Y, 9, 23), datetime(Y, 12, 20))),
        ("winter", (datetime(Y, 12, 21), datetime(Y, 12, 31))),
    ]
    return next(season for season, (start, end) in seasons if start <= today <= end)


def format_ztime(datetime_string):
    """
    Format Datetime.

    Coming from gophish, we get a datetime in a non-iso format,
    thus we need reformat to iso.
    """
    t = datetime.strptime(datetime_string.split(".")[0], "%Y-%m-%dT%H:%M:%S")
    t = t + timedelta(microseconds=int(datetime_string.split(".")[1][:-1]) / 1000)
    return t


def format_timedelta(td: timedelta):
    """
    Format time delta.

    x days, x hours, x minutes
    """
    ret_val = ""
    if td:
        seconds_left_after_hours = td.seconds
        if td.days:
            plural = "s" if td.days not in (0, 1) else ""
            ret_val += f"{td.days} day{plural}, "
        if td.seconds / 3600 >= 1:
            hours = int(math.floor(td.seconds / 3600))
            plural = "s" if hours not in (0, 1) else ""
            ret_val += f"{hours} hour{plural}, "
            seconds_left_after_hours = td.seconds - (hours * 3600)
        if seconds_left_after_hours >= 60:
            minutes = int(seconds_left_after_hours / 60)
            plural = "s" if minutes not in (0, 1) else ""
            seconds_left_after_hours = seconds_left_after_hours - (minutes * 60)
            ret_val += f"{minutes} minute{plural}, "
        if seconds_left_after_hours > 0:
            plural = "s" if td.seconds not in (0, 1) else ""
            ret_val += f"{seconds_left_after_hours} second{plural}, "
    return ret_val.rstrip(" ,")


def display_date(date):
    """Localize a datetime for display."""
    if not timezone.is_aware(date):
        return pytz.UTC.localize(date)
    return date


def parse_time(time):
    """Parse a time."""
    if type(time) is str:
        return dateutil.parser.parse(time)
    return time


def format_json(o):
    """Format Json."""
    if isinstance(o, datetime):
        return o.isoformat()
    else:
        return str(o)


def batch(input_list, n):
    """Divide list evenly through n batches."""
    batches = []
    avg = len(input_list) / float(n)
    last = 0.0
    while last < len(input_list):
        batches.append(input_list[int(last) : int(last + avg)])
        last += avg
    return batches
