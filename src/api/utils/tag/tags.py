"""Tag Utils."""
# Standard Python Libraries
import re

# Third-Party Libraries
from faker import Faker


def check_tag_format(tag):
    """Check_tag_format.

    Checks if the given string is in the format required for a tag.
    Correct: <%TEST_TAG%>
    Args:
        tag (string): Tag string from tag object

    Returns:
        bool: True if in correct format, false otherwise.
    """
    r = re.compile("<%.*%>")
    if r.match(tag) is not None and tag.isupper():
        return True
    return False


def get_faker_tags(with_values: bool = False):
    """Get Faker Tags."""
    fake = Faker()
    tags = []

    funcs = [
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

    for func in funcs:
        tag = {
            "data_source": f"faker_{func}".lower(),
            "description": f"Faker generated {func}",
            "tag": f"<%FAKER_{func.upper()}%>",
            "tag_type": "con-pca-eval",
        }
        if with_values:
            tag["value"] = str(getattr(fake, func)())

        tags.append(tag)
    return tags
