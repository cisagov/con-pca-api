"""Stats page views."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.services import SubscriptionService
from api.utils.generic import format_timedelta
from api.utils.reports import is_nonhuman_request
from api.utils.stats import deception_stats_to_graph_format, get_subscription_cycle
from api.views.reports.cycle_report_views import get_cycle_stats

subscription_service = SubscriptionService()


class CycleStatusView(APIView):
    """CycleStatusView."""

    def get(self, request, subscription_uuid, cycle_uuid):
        """Get."""
        # Get targeted subscription and associated customer data
        subscription = subscription_service.get(subscription_uuid)
        cycle = get_subscription_cycle(subscription, cycle_uuid)

        # Get statistics for the specified subscription during the specified cycle
        stats = get_cycle_stats(subscription, cycle, is_nonhuman_request(request))
        # get_template_details(subscription_stats["campaign_results"])

        context = {
            "avg_time_to_first_click": format_timedelta(
                stats["stats_all"]["clicked"]["average"]
            ),
            "avg_time_to_first_report": format_timedelta(
                stats["stats_all"]["reported"]["average"]
            ),
            "sent": stats["stats_all"]["sent"]["count"],
            "target_count": cycle["total_targets"],
            "campaign_details": stats["campaign_results"],
            "aggregate_stats": stats["stats_all"],
            # "stats": subscription_stats,
            "levels": deception_stats_to_graph_format(stats),
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)
