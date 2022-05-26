"""Flask request helpers."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from flask import request

# cisagov Libraries
from api.manager import LandingPageManager, TemplateManager
from utils.maxmind import get_asn_org, get_city_country

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
    """Get landing page from a click request."""
    template = template_manager.get(document_id=template_id)

    if subscription.get("landing_page_id"):
        landing_page_id = subscription["landing_page_id"]
    elif template.get("landing_page_id"):
        landing_page_id = template["landing_page_id"]
    else:
        landing_page = landing_page_manager.get(
            filter_data={"is_default_template": True}
        )

    if not landing_page:
        landing_page = landing_page_manager.get(filter_data={})
    else:
        landing_page = landing_page_manager.get(document_id=landing_page_id)

    return landing_page
