"""Time utils."""
# Standard Python Libraries
from datetime import datetime
from types import SimpleNamespace


def current_season():
    """Get Current Season."""
    today = datetime.today()
    today = datetime(today.year, today.month, today.day)
    Y = today.year
    seasons = [
        ("winter", (datetime(Y, 1, 1), datetime(Y, 3, 20))),
        ("spring", (datetime(Y, 3, 21), datetime(Y, 6, 20))),
        ("summer", (datetime(Y, 6, 21), datetime(Y, 9, 22))),
        ("autumn", (datetime(Y, 9, 23), datetime(Y, 12, 20))),
        ("winter", (datetime(Y, 12, 21), datetime(Y, 12, 31))),
    ]
    return next(season for season, (start, end) in seasons if start <= today <= end)


def current_date_long():
    """Get current date."""
    return datetime.today().strftime("%B %d, %Y")


def current_date_short():
    """Get current date."""
    return datetime.today().strftime("%m/%d/%y")


def current_month_num():
    """Get current month number."""
    return datetime.today().strftime("%m")


def current_month_long():
    """Get current month long."""
    return datetime.today().strftime("%B")


def current_month_short():
    """Get current month short."""
    return datetime.today().strftime("%b")


def current_year_long():
    """Get current year long."""
    return datetime.today().strftime("%Y")


def current_year_short():
    """Get current year short."""
    return datetime.today().strftime("%y")


def current_day():
    """Get current day."""
    return datetime.today().strftime("%d")


def get_yearly_minutes():
    """Get yearly minutes."""
    return 525600


def convert_seconds(seconds):
    """Convert seconds to hours, minutes and seconds."""
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    d = {
        "hours": hour,
        "minutes": minutes,
        "seconds": seconds,
        "long": f"{hour} hours, {minutes} minutes, {seconds} seconds",
        "short": f"{str(hour).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}",
    }
    return SimpleNamespace(**d)
