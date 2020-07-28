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
    spoof_domain,
)
from simpleeval import simple_eval

logger = logging.getLogger(__name__)


def personalize_template(customer_info, template_data, sub_data, tag_list):
    """
    Personalize Template.

    This takes costomer info, tempalte data and subscription data
    and genereates custom template text to use in gophosh.
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
    """
    simple_eval_options = {
        "names": {"today": datetime.today(), "customer_info": customer_info},
        "functions": {
            "current_season": current_season,
            "get_full_customer_address": get_full_customer_address,
            "generate_random_name": generate_random_name,
            "customer_spoof_email": customer_spoof_email,
            "spoof_domain": spoof_domain,
        },
    }

    personalized_template_data = []
    for template in template_data:
        cleantext = template["html"]
        subject = template["subject"]

        for tag in tag_list:
            if tag["tag_type"] == "gophish":
                # First check gophish tags
                cleantext = cleantext.replace(tag["tag"], tag["data_source"])
                subject = subject.replace(tag["tag"], tag["data_source"])
            elif tag["tag_type"] == "con-pca-literal":
                # literal replace
                cleantext = cleantext.replace(tag["tag"], tag["data_source"])
                subject = subject.replace(tag["tag"], tag["data_source"])
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
                except Exception as err:
                    logger.info(
                        "tag eval error: {}, tag: {}, data_source: {}".format(
                            err, tag["tag"], tag["data_source"]
                        )
                    )
                    # Upon error, replaces tag with empty string to avoid sending tags in email
                    cleantext = cleantext.replace(tag["tag"], "")
                    subject = subject.replace(tag["tag"], "")
            else:
                # Default literal replace with empty string
                cleantext = cleantext.replace(tag["tag"], "")
                subject = subject.replace(tag["tag"], "")

        template_unique_name = "".join(template["name"].split(" "))
        cleantext += "\n {{.Tracker}} "

        personalized_template_data.append(
            {
                "template_uuid": template["template_uuid"],
                "data": cleantext,
                "name": template_unique_name,
                "subject": subject,
            }
        )

    return personalized_template_data
