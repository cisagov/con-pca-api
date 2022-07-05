"""Flask request helpers."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from flask import request

# cisagov Libraries
from api.manager import LandingPageManager, TemplateManager
from utils.logging import setLogger
from utils.maxmind import get_asn_org, get_city_country

logger = setLogger(__name__)

landing_page_manager = LandingPageManager()
template_manager = TemplateManager()


def get_request_ip():
    """Get request ip."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"]
    else:
        return request.remote_addr


def get_timeline_entry(action):
    """Generate timeline entry for targets clicking/opening."""
    ip = get_request_ip()
    asn_org = get_asn_org(ip)
    city, country = get_city_country(ip)
    return {
        "time": datetime.utcnow(),
        "message": action,
        "details": {
            "user_agent": request.user_agent.string,
            "ip": ip,
            "asn_org": asn_org,
            "city": city,
            "country": country,
        },
    }


def get_landing_page(subscription, template_id):
    """
    Get landing page from a click request.

    If the landing page is not set in subscription,
    get the landing page from the template. If the landing page
    is not set in the template, get the default landing page.
    """
    landing_page_id = ""

    template = template_manager.get(document_id=template_id, fields=["landing_page_id"])

    if subscription.get("landing_page_id"):
        landing_page_id = subscription["landing_page_id"]
        logger.info(f"Subscription landing page has been set with {landing_page_id}")
    elif template.get("landing_page_id"):
        landing_page_id = template["landing_page_id"]
        logger.info(f"Template landing page has been set with {landing_page_id}")

    kwargs = (
        {"document_id": landing_page_id}
        if landing_page_id
        else {"filter_data": {"is_default_template": True}}
    )

    return landing_page_manager.get(**kwargs)
