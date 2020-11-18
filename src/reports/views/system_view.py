"""System Reports View."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.services import CampaignService, CustomerService, SubscriptionService
from reports.utils import (
    append_timeline_moment,
    calc_ratios,
    consolidate_campaign_group_stats,
    format_timedelta,
    generate_campaign_statistics,
    get_gov_group_stats,
    get_unique_moments,
)

campaign_manager = CampaignManager()
customer_service = CustomerService()
subscription_service = SubscriptionService()
campaign_service = CampaignService()


class SystemReportsView(APIView):
    """SystemReportsView."""

    def get(self, request, **kwargs):
        """Get."""
        sub_parameters = {"archived": {"$in": [False, None]}}
        subscriptions = subscription_service.get_list(sub_parameters)

        timeline_status = self._get_timeline_list(subscriptions)

        timeline_item_summary = []
        all_stats = []

        for timeline in timeline_status["timeline_list"]:
            unique_moments = get_unique_moments(timeline)
            for unique_moment in unique_moments:
                append_timeline_moment(unique_moment, timeline_item_summary)
            stats, time_aggregate = generate_campaign_statistics(timeline_item_summary)
            all_stats.append(
                {
                    "campaign_stats": stats,
                    "times": time_aggregate,
                }
            )
            timeline_item_summary = []

        consolidated_stats = consolidate_campaign_group_stats(all_stats)
        consolidated_stats["ratios"] = calc_ratios(consolidated_stats)

        customer_stats = self._get_customer_type_count()

        gov_group_stats = get_gov_group_stats()

        gov_group_stats["fed_stats"]["customer_count"] = customer_stats[
            "federal_customers"
        ]
        gov_group_stats["state_stats"]["customer_count"] = customer_stats[
            "state_customers"
        ]
        gov_group_stats["local_stats"]["customer_count"] = customer_stats[
            "local_customers"
        ]
        gov_group_stats["tribal_stats"]["customer_count"] = customer_stats[
            "tribal_customers"
        ]
        gov_group_stats["private_stats"]["customer_count"] = customer_stats[
            "private_customers"
        ]

        if "average" in consolidated_stats["clicked"]:
            avgTimeToClick = format_timedelta(consolidated_stats["clicked"]["average"])
        else:
            avgTimeToClick = None

        context = {
            "customers_enrolled": customer_stats["customers_enrolled"],
            "monthly_reports_sent": timeline_status["monthly_reports_sent"],
            "cycle_reports_sent": timeline_status["cycle_reports_sent"],
            "yearly_reports_sent": timeline_status["yearly_reports_sent"],
            "federal_stats": gov_group_stats["fed_stats"],
            "state_stats": gov_group_stats["state_stats"],
            "local_stats": gov_group_stats["local_stats"],
            "tribal_territorial_stats": gov_group_stats["tribal_stats"],
            "critical_infrastructure_private_stats": gov_group_stats["private_stats"],
            "click_rate_across_all_customers": consolidated_stats["ratios"][
                "clicked_ratio"
            ],
            "average_time_to_click_all_customers": consolidated_stats["clicked"],
            "avgTimeToClick": avgTimeToClick
            # ["clicked"]["average"],
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)

    def _get_timeline_list(self, subscriptions):
        cycles_started = 0
        monthly_reports_sent = 0
        cycle_reports_sent = 0
        yearly_reports_sent = 0
        timeline_list = []

        for sub in subscriptions:
            for notification in sub.get("email_report_history", []):
                if notification["report_type"] == "Cycle Start Notification":
                    cycles_started += 1
                if notification["report_type"] == "Monthly":
                    monthly_reports_sent += 1
                if notification["report_type"] == "Cycle":
                    cycle_reports_sent += 1
                if notification["report_type"] == "Yearly":
                    yearly_reports_sent += 1

            subscription_campaigns = campaign_service.get_list(
                {"subscription_uuid": sub["subscription_uuid"]}
            )

            for campaign in subscription_campaigns:
                timeline_list.append(campaign["timeline"])

        return {
            "cycles_started": cycles_started,
            "monthly_reports_sent": monthly_reports_sent,
            "cycle_reports_sent": cycle_reports_sent,
            "yearly_reports_sent": yearly_reports_sent,
            "timeline_list": timeline_list,
        }

    def _get_customer_type_count(self):
        customers = customer_service.get_list()
        federal_customers = 0
        state_customers = 0
        local_customers = 0
        tribal_customers = 0
        private_customers = 0

        for customer in customers:
            if customer["customer_type"]:
                if customer["customer_type"] == "FED":
                    federal_customers += 1
                if customer["customer_type"] == "State":
                    state_customers += 1
                if customer["customer_type"] == "Local":
                    local_customers += 1
                if customer["customer_type"] == "Tribal":
                    tribal_customers += 1
                if customer["customer_type"] == "Private":
                    private_customers += 1
        return {
            "customers_enrolled": len(customers),
            "federal_customers": federal_customers,
            "state_customers": state_customers,
            "local_customers": local_customers,
            "tribal_customers": tribal_customers,
            "private_customers": private_customers,
        }


class SubsriptionReportsListView(APIView):
    """SubsriptionReportsListView."""

    def get(self, request, **kwargs):
        """Get."""
        subscription_uuid = self.kwargs["subscription_uuid"]
        subscription = subscription_service.get(subscription_uuid)
        context = subscription["email_report_history"]

        return Response(context, status=status.HTTP_202_ACCEPTED)
