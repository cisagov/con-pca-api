"""Tag utils."""
# Third-Party Libraries
from faker import Faker
from utils import customer, time

fake = Faker()


def get_url():
    """Get url."""
    return "Url"


def get_target_first_name():
    """Get target firstname."""
    return "Firstname"


def get_target_last_name():
    """Get target lastname."""
    return "Lastname"


def get_target_full_name():
    """Get target fullname."""
    return "Firstname Lastname"


def get_target_email():
    """Get target email."""
    return "email"


def get_target_position():
    """Get target position."""
    return "position"


TAGS = [
    {
        "func": get_url,
        "description": "A URL which is used to navigate to a web page.",
        "tag": "<%URL%>",
    },
    {
        "data_source": get_target_first_name,
        "description": "The first name of the email recipient.",
        "tag": "<%TARGET_FIRST_NAME%>",
    },
    {
        "data_source": get_target_last_name,
        "description": "The last name of the email recipient.",
        "tag": "<%TARGET_LAST_NAME%>",
    },
    {
        "data_source": get_target_full_name,
        "description": "The full name (first and last) of the email recipient.",
        "tag": "<%TARGET_FULL_NAME%>",
    },
    {
        "data_source": get_target_email,
        "description": "The email address of the recipient.",
        "tag": "<%TARGET_EMAIL%>",
    },
    {
        "data_source": get_target_position,
        "description": "The recipient's job role/position in the organization.",
        "tag": "<%TARGET_POSITION%>",
    },
    {
        "data_source": customer.get_customer_name,
        "description": "The name of the customer organization.",
        "tag": "<%CUSTOMER_NAME%>",
    },
    {
        "data_source": customer.get_customer_identifier,
        "description": "An abbreviated form of a phrase, such as a company/organization's name (i.e. CISA for Cybersecurity and Infrastructure Security Agency).",
        "tag": "<%CUSTOMER_IDENTIFIER%>",
    },
    {
        "data_source": customer.get_full_customer_address,
        "description": "The customer organization's full address including the building number, street name, suite/building, city, state, and zip code.",
        "tag": "<%CUSTOMER_ADDRESS_FULL%>",
    },
    {
        "data_source": customer.get_customer_state,
        "description": "The state where the customer organization is located.",
        "tag": "<%CUSTOMER_STATE%>",
    },
    {
        "data_source": customer.get_customer_city,
        "description": "The city where the customer organization is located.",
        "tag": "<%CUSTOMER_CITY%>",
    },
    {
        "data_source": customer.get_customer_zip,
        "description": "The zip code corresponding to the customer organization location.",
        "tag": "<%CUSTOMER_ZIPCODE%>",
    },
    {
        "data_source": "current_season()",
        "description": "The time of year. This includes summer (June, July, and August), fall (September, October, and November), winter (December, January, and February), and spring (March, April, and May).",
        "tag": time.current_season,
    },
    {
        "data_source": time.current_date_long,
        "description": "The current date written out in full (i.e. March 4th, 2020).",
        "tag": "<%CURRENT_DATE_LONG%>",
    },
    {
        "data_source": time.current_date_short,
        "description": "The current date written out in a shortened format (i.e. 12/27/19).",
        "tag": "<%CURRENT_DATE_SHORT%>",
    },
    {
        "data_source": time.current_month_num,
        "description": "The number corresponding to the current month (1-12 for January-December).",
        "tag": "<%CURRENT_MONTH_NUM%>",
    },
    {
        "data_source": time.current_month_long,
        "description": "The name of the current month written out fully.",
        "tag": "<%CURRENT_MONTH_LONG%>",
    },
    {
        "data_source": time.current_month_short,
        "description": "The name of the current month written out as an abbreviation (i.e. Jan, Feb, Mar, etc.).",
        "tag": "<%CURRENT_MONTH_SHORT%>",
    },
    {
        "data_source": time.current_year_long,
        "description": "The current year written out in full (i.e. 2020).",
        "tag": "<%CURRENT_YEAR_LONG%>",
    },
    {
        "data_source": time.current_year_short,
        "description": "The current year written out in a shortened format (i.e. 19 for 2019).",
        "tag": "<%CURRENT_YEAR_SHORT%>",
    },
    {
        "data_source": time.current_day,
        "description": "The current day of the week.",
        "tag": "<%CURRENT_DAY%>",
    },
]

for faker_func in [
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
]:
    tag = {
        "data_source": fake.__getattr__(faker_func),
        "description": f"Faker generated {faker_func}",
        "tag": f"<%FAKER_{faker_func.upper()}%>",
    }
    TAGS.append(tag)
