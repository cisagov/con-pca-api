"""Tag utils."""
# cisagov Libraries
from utils.fake import FAKER_FUNCS

TAGS = [
    {
        "description": "A URL which is used to navigate to a web page.",
        "tag": "{{url}}",
    },
    {
        "description": "The first name of the email recipient.",
        "tag": "{{target['first_name']}}",
    },
    {
        "description": "The last name of the email recipient.",
        "tag": "{{target['last_name']}}",
    },
    {
        "description": "The email address of the recipient.",
        "tag": "{{target['email']}}",
    },
    {
        "description": "The recipient's job role/position in the organization.",
        "tag": "{{target['position']}}",
    },
    {
        "description": "The name of the customer organization.",
        "tag": "{{customer['name']}}",
    },
    {
        "description": "The customer domain.",
        "tag": "{{customer['domain']}}",
    },
    {
        "description": "An abbreviated form of a phrase, such as a company/organization's name (i.e. CISA for Cybersecurity and Infrastructure Security Agency).",
        "tag": "{{customer['identifier']}}",
    },
    {
        "description": "The state where the customer organization is located.",
        "tag": "{{customer['state']}}",
    },
    {
        "description": "The city where the customer organization is located.",
        "tag": "{{customer['city']}}",
    },
    {
        "description": "The zip code corresponding to the customer organization location.",
        "tag": "{{customer['zip_code']}}",
    },
    {
        "description": "The time of year. This includes summer (June, July, and August), fall (September, October, and November), winter (December, January, and February), and spring (March, April, and May).",
        "tag": "{{time.current_season()}}",
    },
    {
        "description": "The current date written out in full (i.e. March 4th, 2020).",
        "tag": "{{time.current_date_long()}}",
    },
    {
        "description": "The current date written out in a shortened format (i.e. 12/27/19).",
        "tag": "{{time.current_date_short()}}",
    },
    {
        "description": "The number corresponding to the current month (1-12 for January-December).",
        "tag": "{{time.current_month_num()}}",
    },
    {
        "description": "The name of the current month written out fully.",
        "tag": "{{time.current_month_long()}}",
    },
    {
        "description": "The name of the current month written out as an abbreviation (i.e. Jan, Feb, Mar, etc.).",
        "tag": "{{time.current_month_short()}}",
    },
    {
        "description": "The current year written out in full (i.e. 2020).",
        "tag": "{{time.current_year_long()}}",
    },
    {
        "description": "The current year written out in a shortened format (i.e. 19 for 2019).",
        "tag": "{{time.current_year_short()}}",
    },
    {
        "description": "The current day of the week.",
        "tag": "{{time.current_day()}}",
    },
]

for faker_func in FAKER_FUNCS:
    tag = {
        "description": f"Faker generated {faker_func}.",
        "tag": f"{{{{fake.{faker_func}}}}}",
    }
    TAGS.append(tag)
