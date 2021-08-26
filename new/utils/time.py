"""Time utils."""
# Standard Python Libraries
from datetime import datetime


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
