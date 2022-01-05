"""Flask request helpers."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from flask import request

# cisagov Libraries
from utils.maxmind import get_asn_org, get_city_country


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
