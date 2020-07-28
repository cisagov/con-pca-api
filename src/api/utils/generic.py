"""Util Generic."""
# Standard Python Libraries
from datetime import datetime, timedelta

# Third-Party Libraries
from faker import Faker
import names


def current_season():
    """
    Current Season.

    This returns the current season of given Date.
    """
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


def generate_random_name(name_type, gender=None):
    """Generate random name.

    This uses Python package `names`
    to genrate names.
    See https://pypi.org/project/names/ for more info.
    Args:
        name_type (string): name type: 'Full', 'First', 'Last'
        gender (string, optional): can be either either 'male', 'female'. Defaults to None.

    Returns:
        string: returns randomly genrated name string.
    """
    if name_type == "Full":
        return names.get_full_name(gender=gender)
    elif name_type == "First":
        return names.get_first_name(gender=gender)
    elif name_type == "Last":
        return names.get_last_name()


def customer_spoof_email(customer_info):
    """Customer Spoof Email.

    Grabs email domain from customer list and
    creates random spoofed email.
    Args:
        customer_info (dict): customer info dict

    Returns:
        string: returns spoofed email with customer email domain.
    """
    spoof_first_name = names.get_first_name()
    spoof_last_name = names.get_last_name()
    _, customer_domain = customer_info["contact_list"][0].split("@")
    spoof_email = "{}.{}@{}".format(spoof_first_name, spoof_last_name, customer_domain)
    return spoof_email


def spoof_domain():
    """Spoof Domain.

    Returns:
        string: returns fake domain string.
    """
    fake = Faker()
    return fake.domain_name()
