"""System Reports View."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.services import CampaignService, CustomerService, SubscriptionService
from api.utils import stats
from api.utils.generic import format_timedelta

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

        report_history = self.get_report_history(subscriptions)
        campaign_stats = self.get_campaign_stats(subscriptions)

        overall_stats = stats.process_overall_stats(campaign_stats)
        stats.clean_stats(overall_stats)

        categorized_stats = self.get_categorized_stats()

        context = {
            "customers_enrolled": categorized_stats["all_stats"]["customer_count"],
            "monthly_reports_sent": report_history["monthly_reports_sent"],
            "cycle_reports_sent": report_history["cycle_reports_sent"],
            "yearly_reports_sent": report_history["yearly_reports_sent"],
            "federal_stats": categorized_stats["fed_stats"],
            "state_stats": categorized_stats["state_stats"],
            "local_stats": categorized_stats["local_stats"],
            "tribal_territorial_stats": categorized_stats["tribal_stats"],
            "critical_infrastructure_private_stats": categorized_stats["private_stats"],
            "click_rate_across_all_customers": overall_stats["stats_all"]["ratios"][
                "clicked_ratio"
            ],
            "average_time_to_click_all_customers": overall_stats["stats_all"][
                "clicked"
            ],
            "avgTimeToClick": format_timedelta(
                overall_stats["stats_all"]["clicked"]["average"]
            ),
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)

    def get_report_history(self, subscriptions):
        """Get history for reports sent."""
        cycles_started = 0
        monthly_reports_sent = 0
        cycle_reports_sent = 0
        yearly_reports_sent = 0

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

        return {
            "cycles_started": cycles_started,
            "monthly_reports_sent": monthly_reports_sent,
            "cycle_reports_sent": cycle_reports_sent,
            "yearly_reports_sent": yearly_reports_sent,
        }

    def get_campaign_stats(self, subscriptions, nonhuman=False):
        """Get stats for all campaigns in a list of subscriptions."""
        campaign_stats = []
        for subscription in subscriptions:
            campaigns = campaign_service.get_list(
                {"subscription_uuid": subscription["subscription_uuid"]}
            )
            for campaign in campaigns:
                campaign_stats.append(stats.process_campaign(campaign, nonhuman))
        return campaign_stats

    def get_categorized_stats(self):
        """Get base stats for all related subscriptions (national, sector, industry, and customer)."""
        customers = customer_service.get_list()

        fed_customer_uuids = []
        state_customer_uuids = []
        local_customer_uuids = []
        tribal_customer_uuids = []
        private_customer_uuids = []

        for cust in customers:
            if cust["customer_type"] == "FED":
                fed_customer_uuids.append(cust["customer_uuid"])
            if cust["customer_type"] == "State":
                state_customer_uuids.append(cust["customer_uuid"])
            if cust["customer_type"] == "Local":
                local_customer_uuids.append(cust["customer_uuid"])
            if cust["customer_type"] == "Tribal":
                tribal_customer_uuids.append(cust["customer_uuid"])
            if cust["customer_type"] == "Private":
                private_customer_uuids.append(cust["customer_uuid"])

        subscription_list = subscription_service.get_list()

        fed_subscriptions = []
        state_subscriptions = []
        local_subscriptions = []
        tribal_subscriptions = []
        private_subscriptions = []

        fed_subscriptions = list(
            filter(
                lambda x: x["customer_uuid"] in fed_customer_uuids, subscription_list
            )
        )
        state_subscriptions = list(
            filter(
                lambda x: x["customer_uuid"] in state_customer_uuids, subscription_list
            )
        )
        local_subscriptions = list(
            filter(
                lambda x: x["customer_uuid"] in local_customer_uuids, subscription_list
            )
        )
        tribal_subscriptions = list(
            filter(
                lambda x: x["customer_uuid"] in tribal_customer_uuids, subscription_list
            )
        )
        private_subscriptions = list(
            filter(
                lambda x: x["customer_uuid"] in private_customer_uuids,
                subscription_list,
            )
        )

        data = {
            "all_stats": stats.get_simple_stats_from_subscriptions(subscription_list),
            "fed_stats": stats.get_simple_stats_from_subscriptions(fed_subscriptions),
            "state_stats": stats.get_simple_stats_from_subscriptions(
                state_subscriptions
            ),
            "local_stats": stats.get_simple_stats_from_subscriptions(
                local_subscriptions
            ),
            "tribal_stats": stats.get_simple_stats_from_subscriptions(
                tribal_subscriptions
            ),
            "private_stats": stats.get_simple_stats_from_subscriptions(
                private_subscriptions
            ),
        }

        data["fed_stats"]["customer_count"] = len(local_customer_uuids)
        data["state_stats"]["customer_count"] = len(state_customer_uuids)
        data["local_stats"]["customer_count"] = len(local_customer_uuids)
        data["tribal_stats"]["customer_count"] = len(tribal_customer_uuids)
        data["private_stats"]["customer_count"] = len(private_customer_uuids)
        data["all_stats"]["customer_count"] = len(customers)

        return data


class SubsriptionReportsListView(APIView):
    """SubsriptionReportsListView."""

    def get(self, request, **kwargs):
        """Get."""
        subscription_uuid = self.kwargs["subscription_uuid"]
        subscription = subscription_service.get(
            subscription_uuid, fields=["email_report_history"]
        )
        context = subscription["email_report_history"]

        return Response(context, status=status.HTTP_202_ACCEPTED)
