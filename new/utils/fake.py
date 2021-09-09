"""Fake util."""
# Third-Party Libraries
from faker import Faker

FAKER_FUNCS = [
    "address",
    "am_pm",
    "building_number",
    "city",
    "color_name",
    "company",
    "company_email",
    "country",
    "credit_card_number",
    "credit_card_provider",
    "credit_card_security_code",
    "day_of_month",
    "day_of_week",
    "domain_name",
    "email",
    "first_name",
    "first_name_female",
    "first_name_male",
    "hostname",
    "invalid_ssn",
    "job",
    "last_name",
    "last_name_female",
    "last_name_male",
    "license_plate",
    "month",
    "month_name",
    "name",
    "name_female",
    "name_male",
    "password",
    "phone_number",
    "postalcode",
    "random_digit",
    "random_int",
    "random_letter",
    "random_lowercase_letter",
    "random_number",
    "random_uppercase_letter",
    "state",
    "state_abbr",
    "street_address",
    "street_name",
    "street_suffix",
    "user_name",
    "year",
    "zip",
    "zipcode",
]


class Fake:
    """Fake."""

    def __init__(self):
        """Initialize fake class."""
        f = Faker()
        for faker_func in FAKER_FUNCS:
            setattr(self, faker_func, getattr(f, faker_func)())
