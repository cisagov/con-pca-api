"""Template Utils file for api."""
# Standard Python Libraries
from datetime import datetime
import logging

# Third-Party Libraries
from api.utils.customer.customers import get_full_customer_address
from api.utils.generic import (
    current_season,
    customer_spoof_email,
    generate_random_name,
)
from api.utils.faker.faker_util import FakerUtil
from simpleeval import simple_eval

logger = logging.getLogger(__name__)


def personalize_template(customer_info, template_data, sub_data, tag_list):
    """
    Personalize Template.

    This takes customer info, tempalte data and subscription data
    and genereates custom template text to use in gophish.
    It also fills in GoPhish usable params.
    Below are old replace tags for refrence:

    check_replace = {
        "<%CUSTOMER_NAME%>": customer_info["name"],
        "<%CUSTOMER_ADDRESS_FULL%>": customer_full_address(customer_info),
        "<%CUSTOMER_ADDRESS_1%>": customer_info["address_1"],
        "<%CUSTOMER_ADDRESS_2%>": customer_info["address_2"],
        "<%CUSTOMER_STATE%>": customer_info["state"],
        "<%CUSTOMER_CITY%>": customer_info["city"],
        "<%CUSTOMER_ZIPCODE%>": customer_info["zip_code"],
        "<%CURRENT_SEASON%>": current_season(),
        "<%CURRENT_DATE_LONG%>": today.strftime("%B %d, %Y"),
        "<%CURRENT_DATE_SHORT%>": today.strftime("%m/%d/%y"),
        "<%CURRENT_MONTH_NUM%>": today.strftime("%m"),
        "<%CURRENT_MONTH_LONG%>": today.strftime("%B"),
        "<%CURRENT_MONTH_SHORT%>": today.strftime("%b"),
        "<%CURRENT_YEAR_LONG%>": today.strftime("%Y"),
        "<%CURRENT_YEAR_SHORT%>": today.strftime("%y"),
        "<%CURRENT_DAY%>": today.strftime("%d"),
        "<%SPOOF_NAME%>": "FAKE NAME GERNERATOR",
        "<%EVENT%>": "Relevent Event",
        "<%TIMEFRAME%>": "Relevent Timeframe",
    }
    gophish_tags = {
        "<%URL%>": "{{.URL}}",
        "<%TARGET_FIRST_NAME%>": "{{.FirstName}}",
        "<%TARGET_LAST_NAME%>": "{{.LastName}}",
        "<%TARGET_FULLL_NAME%>": "{{.FirstName}} {{.LastName}}",
        "<%TARGET_EMAIL%>": "{{.Email}}",
        "<%TARGET_POSITION%>": "{{.Position}}",
        "<%FROM%>": "{{.From}}"
    }
     faker_tags = {
        "<%FAKER_[Faker Property]%>": "[Faker Property]"
    }
    """

    faker = FakerUtil

    simple_eval_options = {
        "names": {"today": datetime.today(), "customer_info": customer_info},
        "functions": {
            "current_season": current_season,
            "get_full_customer_address": get_full_customer_address,
            "generate_random_name": generate_random_name,
            "customer_spoof_email": customer_spoof_email,
            "building_number": faker.address.building_number,
            "city": faker.address.city,
            "city_suffix": faker.address.city_suffix,
            "country": faker.address.country,
            "country_code": faker.address.country_code,
            "postcode": faker.address.postcode,
            "street_address": faker.address.street_address,
            "street_name": faker.address.street_name,
            "street_suffix": faker.address.street_suffix,
            "license_plate": faker.automotive.license_plate,
            "color": faker.color.color,
            "color_name": faker.color.color_name,
            "hex_color": faker.color.hex_color,
            "rgb_color": faker.color.rgb_color,
            "rgb_css_color": faker.color.rgb_css_color,
            "safe_color_name": faker.color.safe_color_name,
            "safe_hex_color": faker.color.safe_hex_color,
            "bs": faker.company.bs,
            "catch_phrase": faker.company.catch_phrase,
            "company": faker.company.company,
            "company_suffix": faker.company.company_suffix,
            "credit_card_expire": faker.credit_card.credit_card_expire,
            "credit_card_full": faker.credit_card.credit_card_full,
            "credit_card_number": faker.credit_card.credit_card_number,
            "credit_card_provider": faker.credit_card.credit_card_provider,
            "credit_card_security_code": faker.credit_card.credit_card_security_code,
            "cryptocurrency_name": faker.currency.cryptocurrency_name,
            "cryptocurrency_code": faker.currency.cryptocurrency_code,
            "currency_code": faker.currency.currency_code,
            "currency_name": faker.currency.currency_name,
            "currency_symbol": faker.currency.currency_symbol,
            "file_extension": faker.file.file_extension,
            "file_name": faker.file.file_name,
            "file_path": faker.file.file_path,
            "mime_type": faker.file.mime_type,
            "unix_device": faker.file.unix_device,
            "unix_partition": faker.file.unix_partition,
            "ascii_company_email": faker.internet.ascii_company_email,
            "ascii_email": faker.internet.ascii_email,
            "ascii_free_email": faker.internet.ascii_free_email,
            "company_email": faker.internet.company_email,
            "domain_name": faker.internet.domain_name,
            "email": faker.internet.email,
            "free_email": faker.internet.free_email,
            "hostname": faker.internet.hostname,
            "image_url": faker.internet.image_url,
            "ipv4": faker.internet.ipv4,
            "ipv6": faker.internet.ipv6,
            "mac_address": faker.internet.mac_address,
            "user_name": faker.internet.user_name,
            "url": faker.internet.url,
            "uri": faker.internet.uri,
            "safe_email": faker.internet.safe_email,
            "safe_domain_name": faker.internet.safe_domain_name,
            "isbn10": faker.isbn.isbn10,
            "isbn13": faker.isbn.isbn13,
            "position": faker.job.position,
            "paragraph": faker.lorem.paragraph,
            "sentence": faker.lorem.sentence,
            "text": faker.lorem.text,
            "first_name": faker.person.first_name,
            "first_name_female": faker.person.first_name_female,
            "first_name_male": faker.person.first_name_male,
            "first_name_nonbinary": faker.person.first_name_nonbinary,
            "language_name": faker.person.language_name,
            "last_name": faker.person.last_name,
            "last_name_female": faker.person.last_name_female,
            "last_name_male": faker.person.last_name_male,
            "last_name_nonbinary": faker.person.last_name_nonbinary,
            "name": faker.person.name,
            "name_female": faker.person.name_female,
            "name_male": faker.person.name_male,
            "name_nonbinary": faker.person.name_nonbinary,
            "prefix": faker.person.prefix,
            "prefix_female": faker.person.prefix_female,
            "prefix_male": faker.person.prefix_male,
            "prefix_nonbinary": faker.person.prefix_nonbinary,
            "suffix": faker.person.suffix,
            "suffix_female": faker.person.suffix_female,
            "suffix_male": faker.person.suffix_male,
            "ssn": faker.person.ssn,
            "country_calling_code": faker.phone.country_calling_code,
            "phone_number": faker.phone.phone_number,
            "msisdn": faker.phone.msisdn,
        },
    }

    personalized_template_data = []
    for template in template_data:
        cleantext = template["html"]
        subject = template["subject"]
        from_address = template["from_address"]

        for tag in tag_list:
            if tag["tag_type"] == "gophish":
                # First check gophish tags
                cleantext = cleantext.replace(tag["tag"], tag["data_source"])
                subject = subject.replace(tag["tag"], tag["data_source"])
                from_address = from_address.replace(tag["tag"], tag["data_source"])
            elif tag["tag_type"] == "con-pca-literal":
                # literal replace
                cleantext = cleantext.replace(tag["tag"], tag["data_source"])
                subject = subject.replace(tag["tag"], tag["data_source"])
                from_address = from_address.replace(tag["tag"], tag["data_source"])
            elif tag["tag_type"] == "con-pca-eval":
                # eval replace
                try:
                    # ast.literal_eval(tag["data_source"]) replaced with smarter eval
                    cleantext = cleantext.replace(
                        tag["tag"],
                        simple_eval(
                            tag["data_source"],
                            names=simple_eval_options["names"],
                            functions=simple_eval_options["functions"],
                        ),
                    )
                    subject = subject.replace(
                        tag["tag"],
                        simple_eval(
                            tag["data_source"],
                            names=simple_eval_options["names"],
                            functions=simple_eval_options["functions"],
                        ),
                    )
                    from_address = from_address.replace(
                        tag["tag"],
                        simple_eval(
                            tag["data_source"],
                            names=simple_eval_options["names"],
                            functions=simple_eval_options["functions"],
                        ),
                    )
                except Exception as err:
                    logger.info(
                        "tag eval error: {}, tag: {}, data_source: {}".format(
                            err, tag["tag"], tag["data_source"]
                        )
                    )
                    # Upon error, replaces tag with empty string to avoid sending tags in email
                    cleantext = cleantext.replace(tag["tag"], "")
                    subject = subject.replace(tag["tag"], "")
                    from_address = from_address.replace(tag["tag"], "")
            else:
                # Default literal replace with empty string
                cleantext = cleantext.replace(tag["tag"], "")
                subject = subject.replace(tag["tag"], "")
                from_address = from_address.replace(tag["tag"], "")

        template_unique_name = "".join(template["name"].split(" "))
        cleantext += "\n {{.Tracker}} "

        landing_page_uuid = ""
        if "landing_page_uuid" in template:
            landing_page_uuid = template["landing_page_uuid"]

        personalized_template_data.append(
            {
                "template_uuid": template["template_uuid"],
                "data": cleantext,
                "name": template_unique_name,
                "from_address": from_address,
                "subject": subject,
                "landing_page_uuid": landing_page_uuid,
            }
        )

    return personalized_template_data
