"""Generic Util Tests."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from src.api.utils import generic

fake = Faker()


def test_current_season():
    """Test Current Season."""
    season = generic.current_season()
    assert type(season) is str
    assert season in ["winter", "spring", "summer", "autumn"]


def test_format_ztime():
    """Test Format Ztime."""
    t = fake.date_time().strftime("%Y-%m-%dT%H:%M:%S.%f")
    result = generic.format_ztime(t)
    assert type(result) is datetime
