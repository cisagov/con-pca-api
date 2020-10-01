from src.api.utils import generic
from faker import Faker
import re
from datetime import datetime

fake = Faker()


def test_current_season():
    season = generic.current_season()
    assert type(season) is str
    assert season in ["winter", "spring", "summer", "autumn"]


def test_format_ztime():
    t = fake.date_time().strftime("%Y-%m-%dT%H:%M:%S.%f")
    result = generic.format_ztime(t)
    assert type(result) is datetime


def test_customer_spoof_email():
    domain = fake.domain_name()
    customer_info = {"contact_list": [{"email": f"test@{domain}"}]}
    result = generic.customer_spoof_email(customer_info)
    assert re.match(fr"^\w+.\w+@{domain}$", result)
