# Standard Python Libraries
import base64
from datetime import datetime, timedelta
import logging

# Third-Party Libraries


from api.manager import CampaignManager
from api.models.customer_models import CustomerModel, validate_customer
from api.models.dhs_models import DHSContactModel, validate_dhs_contact
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.utils.db_utils import get_list, get_single
from django.views.generic import TemplateView

# Local Libraries
# Django Libraries
from reports.utils import (
    append_timeline_moment,
    calc_ratios,
    campaign_templates_to_string,
    consolidate_campaign_group_stats,
    format_timedelta,
    generate_campaign_statistics,
    generate_region_stats,
    get_closest_cycle_within_day_range,
    get_cycle_by_date_in_range,
    get_cycles_breakdown,
    get_gov_group_stats,
    get_most_successful_campaigns,
    get_related_subscription_stats,
    get_reports_to_click,
    get_statistic_from_group,
    get_statistic_from_region_group,
    get_stats_low_med_high_by_level,
    get_subscription_stats_for_cycle,
    get_subscription_stats_for_month,
    get_template_details,
    pprintItem,
    ratio_to_percent,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Local Libraries
# Django Libraries
from scipy.stats.mstats import gmean

logger = logging.getLogger(__name__)

# GoPhish API Manager
campaign_manager = CampaignManager()


class SystemReportsView(APIView):
    def get(self, request, **kwargs):
        """
        Generate the cycle report based off of the provided start date
        """

        sub_parameters = {"archived": {"$in": [False, None]}}
        subscriptions = get_list(
            sub_parameters, "subscription", SubscriptionModel, validate_subscription
        )

        cycles_started = 0
        monthly_reports_sent = 0
        cycle_reports_sent = 0
        yearly_reports_sent = 0

        _timeline_list = []

        for sub in subscriptions:
            for email_notifcation in sub["email_report_history"]:
                if email_notifcation["report_type"] == "Cycle Start Notification":
                    cycles_started += 1
                if email_notifcation["report_type"] == "Monthly":
                    monthly_reports_sent += 1
                if email_notifcation["report_type"] == "Cycle":
                    cycle_reports_sent += 1
                if email_notifcation["report_type"] == "Yearly":
                    yearly_reports_sent += 1
            for campaign in sub["gophish_campaign_list"]:
                _timeline_list.append(campaign["timeline"])

        timeline_item_summary = []
        all_stats = []

        for timeline in _timeline_list:
            for moment in timeline:
                if not moment["duplicate"]:
                    append_timeline_moment(moment, timeline_item_summary)
            stats, time_aggregate = generate_campaign_statistics(timeline_item_summary)
            all_stats.append(
                {"campaign_stats": stats, "times": time_aggregate,}
            )
            timeline_item_summary = []

        consolidated_stats = consolidate_campaign_group_stats(all_stats)
        consolidated_stats["ratios"] = calc_ratios(consolidated_stats)

        customers = get_list({}, "customer", CustomerModel, validate_customer)
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

        gov_group_stats = get_gov_group_stats()
        gov_group_stats["fed_stats"]["customer_count"] = federal_customers
        gov_group_stats["state_stats"]["customer_count"] = state_customers
        gov_group_stats["local_stats"]["customer_count"] = local_customers
        gov_group_stats["tribal_stats"]["customer_count"] = tribal_customers
        gov_group_stats["private_stats"]["customer_count"] = private_customers

        context = {
            "customers_enrolled": len(customers),
            "monthly_reports_sent": monthly_reports_sent,
            "cycle_reports_sent": cycle_reports_sent,
            "yearly_reports_sent": yearly_reports_sent,
            "federal_stats": gov_group_stats["fed_stats"],
            "state_stats": gov_group_stats["state_stats"],
            "local_stats": gov_group_stats["local_stats"],
            "tribal_territorial_stats": gov_group_stats["tribal_stats"],
            "critical_infrastructure_private_stats": gov_group_stats["private_stats"],
            "click_rate_across_all_customers": consolidated_stats["ratios"][
                "clicked_ratio"
            ],
            "average_time_to_click_all_customers": consolidated_stats["clicked"][
                "average"
            ],
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)
