"""Landing application views."""
# Standard Python Libraries
from datetime import datetime
from pprint import pprint

# Third-Party Libraries
from flask import request, send_file
from flask.templating import render_template_string
from flask.views import MethodView
from utils.maxmind import get_asn_org, get_city_country
from utils.request import get_request_ip

# cisagov Libraries
from api.manager import CycleManager, LandingPageManager, TemplateManager
from api.phish import decode_tracking_id

cycle_manager = CycleManager()
template_manager = TemplateManager()
landing_page_manager = LandingPageManager()


class ClickView(MethodView):
    """ClickView."""

    def get(self, tracking_id):
        """Get."""
        pprint(dir(request))
        pprint(request.headers)
        pprint(request.remote_addr)
        cycle_uuid, target_uuid = decode_tracking_id(tracking_id)
        cycle = cycle_manager.get(uuid=cycle_uuid)
        target = next(
            filter(lambda x: x["target_uuid"] == target_uuid, cycle["targets"])
        )
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

        ip = get_request_ip()
        city, country = get_city_country(ip)
        asn_org = get_asn_org(ip)

        # TODO: Check for open event, if not add one.
        cycle_manager.add_timeline_item(
            cycle_uuid=cycle["cycle_uuid"],
            target_uuid=target["target_uuid"],
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

        return render_template_string(landing_page["html"])


class OpenView(MethodView):
    """OpenView."""

    def get(self, tracking_id):
        """Get."""
        cycle_uuid, target_uuid = decode_tracking_id(tracking_id)
        cycle = cycle_manager.get(uuid=cycle_uuid)
        target = next(
            filter(lambda x: x["target_uuid"] == target_uuid, cycle["targets"])
        )
        cycle_manager.add_timeline_item(
            cycle_uuid=cycle["cycle_uuid"],
            target_uuid=target["target_uuid"],
            data={
                "time": datetime.utcnow(),
                "message": "opened",
                "details": {
                    "user_agent": request.user_agent.string,
                    "ip": request.remote_addr,
                    "asn_org": "",
                },
            },
        )
        return send_file("static/pixel.gif", mimetype="image/gif")
