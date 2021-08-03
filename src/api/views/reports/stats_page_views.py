"""Stats page views."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.services import CampaignService, SubscriptionService
from api.utils.generic import format_timedelta
from api.utils.reports import is_nonhuman_request
from api.utils.stats import (
    deception_stats_to_graph_format,
    get_asn_org_stats,
    get_subscription_cycle,
    get_template_details,
)
from api.views.reports.cycle_report_views import get_cycle_stats

subscription_service = SubscriptionService()
campaign_service = CampaignService()


class CycleStatusView(APIView):
    """CycleStatusView."""

    def get(self, request, subscription_uuid, cycle_uuid):
        """Get."""
        # Get targeted subscription and associated customer data
        subscription = subscription_service.get(
            subscription_uuid, fields=["subscription_uuid", "cycles"]
        )
        cycle = get_subscription_cycle(subscription, cycle_uuid)
        subscription["campaigns"] = campaign_service.get_list(
            parameters={"cycle_uuid": cycle_uuid}
        )

        # Get statistics for the specified subscription during the specified cycle
        stats = get_cycle_stats(subscription, cycle, is_nonhuman_request(request))
        get_template_details(stats)
        timeline = []
        for campaign in subscription["campaigns"]:
            timeline.extend(campaign["timeline"])
        asn_stats = get_asn_org_stats(timeline)

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
            "template_breakdown": stats["template_breakdown"],
            # "stats": subscription_stats,
            "levels": deception_stats_to_graph_format(stats),
            "asn_stats": asn_stats,
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)
