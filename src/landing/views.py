"""Landing application views."""
# Third-Party Libraries
from flask import redirect, send_file
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
from utils.request import get_landing_page, get_timeline_entry
from utils.safelist_testing import process_click_test, process_open_test

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
        decoded = decode_tracking_id(tracking_id)
        if len(decoded) > 2:
            if decoded[0] == "test":
                return process_click_test(decoded[1], decoded[2])
            else:
                return
        cycle_id, target_id = decoded
        cycle = cycle_manager.get(
            document_id=cycle_id, fields=["_id", "subscription_id"]
        )
        target = target_manager.get(document_id=target_id)
        if not cycle or not target:
            return render_template_string("404 Not Found"), 404

        click_events = list(
            filter(lambda x: x["message"] == "clicked", target.get("timeline", []))
        )
        if len(click_events) < 10:
            target_manager.add_to_list(
                document_id=target["_id"],
                field="timeline",
                data=get_timeline_entry("clicked"),
            )
            cycle_manager.update(document_id=cycle["_id"], data={"dirty_stats": True})

        # If a landing page url exists for the subscription, redirect to it after click has been tracked
        subscription = subscription_manager.get(
            document_id=cycle["subscription_id"],
            fields=["customer_id", "landing_page_url"],
        )

        if subscription.get("landing_page_url"):
            return redirect(subscription["landing_page_url"], 302)

        customer = customer_manager.get(document_id=subscription["customer_id"])
        landing_page = get_landing_page(target["template_id"])

        context = get_email_context(target=target, customer=customer)
        return render_template_string(landing_page["html"], **context)


class OpenView(MethodView):
    """OpenView."""

    def get(self, tracking_id):
        """Get."""
        decoded = decode_tracking_id(tracking_id)
        if len(decoded) > 2:
            if decoded[0] == "test":
                process_open_test(decoded[1], decoded[2])
                return send_file("static/pixel.gif", mimetype="image/gif")
            else:
                return
        cycle_id, target_id = decoded
        cycle = cycle_manager.get(
            document_id=cycle_id, fields=["_id", "subscription_id"]
        )
        target = target_manager.get(document_id=target_id)
        if not cycle or not target:
            return render_template_string("404 Not Found"), 404

        open_events = list(
            filter(lambda x: x["message"] == "opened", target.get("timeline", []))
        )
        if len(open_events) < 10:
            target_manager.add_to_list(
                document_id=target["_id"],
                field="timeline",
                data=get_timeline_entry("opened"),
            )
            cycle_manager.update(document_id=cycle["_id"], data={"dirty_stats": True})
        return send_file("static/pixel.gif", mimetype="image/gif")
