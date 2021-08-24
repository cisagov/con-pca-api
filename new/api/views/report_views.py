"""Report views."""
# Third-Party Libraries
from flask.templating import render_template
from flask.views import MethodView
from utils.stats import get_cycle_stats

# cisagov Libraries
from api.manager import CustomerManager, CycleManager, SubscriptionManager

subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()
customer_manager = CustomerManager()


class StatusReportView(MethodView):
    """Status report view."""

    def get(self, cycle_uuid):
        """Get."""
        cycle = cycle_manager.get(uuid=cycle_uuid)
        subscription = subscription_manager.get(
            uuid=cycle["subscription_uuid"],
            fields=[
                "subscription_uuid",
                "name",
                "customer_uuid",
                "target_domain",
                "start_date",
                "primary_contact",
                "admin_email",
                "status",
            ],
        )
        customer = customer_manager.get(uuid=subscription["customer_uuid"])
        context = {
            "stats": get_cycle_stats(cycle),
            "cycle": cycle,
            "subscription": subscription,
            "customer": customer,
        }
        return render_template("reports/status.html", **context), 200
