"""Landing application views."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from flask import request, send_file
from flask.templating import render_template_string
from flask.views import MethodView

# cisagov Libraries
from api.manager import (
    CustomerManager,
    CycleManager,
    LandingPageManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from api.phish import decode_tracking_id
from utils.emails import get_email_context
from utils.maxmind import get_asn_org, get_city_country
from utils.request import get_request_ip

cycle_manager = CycleManager()
template_manager = TemplateManager()
landing_page_manager = LandingPageManager()
subscription_manager = SubscriptionManager()
customer_manager = CustomerManager()
target_manager = TargetManager()


class ClickView(MethodView):
    """ClickView."""

    def get(self, tracking_id):
        """Get."""
        cycle_uuid, target_uuid = decode_tracking_id(tracking_id)
        cycle = cycle_manager.get(
            uuid=cycle_uuid, fields=["cycle_uuid", "subscription_uuid"]
        )
        target = target_manager.get(uuid=target_uuid)
        if not cycle or not target:
            return render_template_string("404 Not Found"), 404
        template = template_manager.get(
            uuid=target["template_uuid"], fields=["landing_page_uuid"]
        )
        if template.get("landing_page_uuid"):
            landing_page = landing_page_manager.get(uuid=template["landing_page_uuid"])
        else:
            landing_page = landing_page_manager.get(
                filter_data={"is_default_template": True}
            )
        if not landing_page:
            landing_page = landing_page_manager.get(filter_data={})

        click_events = list(
            filter(lambda x: x["message"] == "clicked", target.get("timeline", []))
        )
        if len(click_events) < 10:
            ip = get_request_ip()
            city, country = get_city_country(ip)
            asn_org = get_asn_org(ip)

            target_manager.add_to_list(
                uuid=target["target_uuid"],
                field="timeline",
                data={
                    "time": datetime.utcnow(),
                    "message": "clicked",
                    "details": {
                        "user_agent": request.user_agent.string,
                        "ip": ip,
                        "asn_org": asn_org,
                        "city": city,
                        "country": country,
                    },
                },
            )
            cycle_manager.update(uuid=cycle["cycle_uuid"], data={"dirty_stats": True})

        subscription = subscription_manager.get(
            uuid=cycle["subscription_uuid"], fields=["customer_uuid"]
        )
        customer = customer_manager.get(uuid=subscription["customer_uuid"])

        context = get_email_context(target=target, customer=customer)
        return render_template_string(landing_page["html"], **context)


class OpenView(MethodView):
    """OpenView."""

    def get(self, tracking_id):
        """Get."""
        cycle_uuid, target_uuid = decode_tracking_id(tracking_id)
        cycle = cycle_manager.get(
            uuid=cycle_uuid, fields=["cycle_uuid", "subscription_uuid"]
        )
        target = target_manager.get(uuid=target_uuid)
        if not cycle or not target:
            return render_template_string("404 Not Found"), 404

        open_events = list(
            filter(lambda x: x["message"] == "opened", target.get("timeline", []))
        )
        if len(open_events) < 10:
            ip = get_request_ip()
            city, country = get_city_country(ip)
            asn_org = get_asn_org(ip)
            target_manager.add_to_list(
                uuid=target["target_uuid"],
                field="timeline",
                data={
                    "time": datetime.utcnow(),
                    "message": "opened",
                    "details": {
                        "user_agent": request.user_agent.string,
                        "ip": ip,
                        "asn_org": asn_org,
                        "city": city,
                        "country": country,
                    },
                },
            )
            cycle_manager.update(uuid=cycle["cycle_uuid"], data={"dirty_stats": True})
        return send_file("static/pixel.gif", mimetype="image/gif")
