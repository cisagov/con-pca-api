# Standard Python Libraries
from datetime import datetime, timedelta
import logging
import base64

# Third-Party Libraries
# Local Libraries
# Django Libraries
from scipy.stats.mstats import gmean
from api.manager import CampaignManager
from api.models.customer_models import CustomerModel, validate_customer
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.models.customer_models import CustomerModel, validate_customer
from api.models.dhs_models import DHSContactModel, validate_dhs_contact
from api.models.recommendations_models import (
    RecommendationsModel,
    validate_recommendations,
)
from api.utils.db_utils import get_list, get_single
import pytz
from django.utils import timezone
from reports.utils import get_relevant_recommendations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import TemplateView


# from . import views
from reports.utils import (
    get_subscription_stats_for_yearly,
    get_related_subscription_stats,
    get_cycles_breakdown,
    get_template_details,
    get_statistic_from_group,
    get_reports_to_click,
    campaign_templates_to_string,
    get_most_successful_campaigns,
    get_closest_cycle_within_day_range,
    ratio_to_percent,
    format_timedelta,
    get_statistic_from_region_group,
    get_stats_low_med_high_by_level,
    get_cycle_by_date_in_range,
    set_cycle_quarters,
    cycle_stats_to_percentage_trend_graph_data,
    cycle_stats_to_click_rate_vs_report_rate,
    determine_trend,
    get_yearly_start_dates,
    pprintItem,
)

logger = logging.getLogger(__name__)

# GoPhish API Manager
campaign_manager = CampaignManager()


class YearlyReportsView(APIView):
    """
    Yearly Reports
    """

    def get(self, request, **kwargs):
        for i in kwargs:
            pprintItem(i)
        subscription_uuid = self.kwargs["subscription_uuid"]
        start_date_param = self.kwargs["start_date"]
        start_date = datetime.strptime(start_date_param, "%Y-%m-%dT%H:%M:%S.%f%z")
        subscription = get_single(
            subscription_uuid, "subscription", SubscriptionModel, validate_subscription
        )
        customer = get_single(
            subscription.get("customer_uuid"),
            "customer",
            CustomerModel,
            validate_customer,
        )

        dhs_contact = get_single(
            subscription.get("dhs_contact_uuid"),
            "dhs_contact",
            DHSContactModel,
            validate_dhs_contact,
        )
        campaigns = subscription.get("gophish_campaign_list")
        # summary = [
        #     campaign_manager.get("summary", campaign_id=campaign.get("campaign_id"))
        #     for campaign in campaigns
        # ]

        cycles = subscription["cycles"]
        set_cycle_quarters(cycles)

        # target_count = sum([targets.get("stats").get("total") for targets in summary])
        target_count = len(subscription["target_email_list"])

        yearly_start_date, yearly_end_date = get_yearly_start_dates(
            subscription, start_date
        )

        # Get subscription stats for the previous year.
        # Provide date values to get_subscription_stats_for_yearly for a different time span
        subscription_stats, cycles_stats = get_subscription_stats_for_yearly(
            subscription
        )
        region_stats = get_related_subscription_stats(subscription)
        percentage_trends_data = cycle_stats_to_percentage_trend_graph_data(
            cycles_stats
        )
        clickrate_vs_reportrate_data = cycle_stats_to_click_rate_vs_report_rate(
            cycles_stats
        )
        trend = determine_trend(cycles_stats)
    
        customer_address = """
        {} {},
        {} USA {}
        """.format(
            customer.get("address_1"),
            customer.get("address_2"),
            customer.get("state"),
            customer.get("zip_code"),
        )

        dhs_contact_name = "{} {}".format(
            dhs_contact.get("first_name"), dhs_contact.get("last_name")
        )

        metrics = {
            "total_users_targeted": len(subscription["target_email_list"]),
            "number_of_email_sent_overall": get_statistic_from_group(
                subscription_stats, "stats_all", "sent", "count"
            ),
            "customer_clicked_avg": ratio_to_percent(
                get_statistic_from_region_group(
                    region_stats, "customer", "clicked_ratio"
                ),
                0,
            ),
            "national_clicked_avg": ratio_to_percent(
                get_statistic_from_region_group(
                    region_stats, "national", "clicked_ratio"
                ),
                0,
            ),
            "industry_clicked_avg": ratio_to_percent(
                get_statistic_from_region_group(
                    region_stats, "industry", "clicked_ratio"
                ),
                0,
            ),
            "sector_clicked_avg": ratio_to_percent(
                get_statistic_from_region_group(
                    region_stats, "sector", "clicked_ratio"
                ),
                0,
            ),
            "shortest_time_to_report": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "reported", "minimum"
                )
            ),
            "median_time_to_report": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "reported", "median"
                )
            ),
            "shortest_time_to_open": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "opened", "minimum"
                )
            ),
            "median_time_to_open": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "opened", "median"
                )
            ),
            "longest_time_to_open": format_timedelta(
                get_statistic_from_group(
                    subscription_stats, "stats_all", "opened", "maximum"
                )
            ),
        }
        get_template_details(subscription_stats["campaign_results"])
        recommendation_uuids = get_relevant_recommendations(subscription_stats)

        _recomendations = get_list(
            None, "recommendations", RecommendationsModel, validate_recommendations,
        )
        recomendations = []
        for rec in _recomendations:
            if rec["recommendations_uuid"] in recommendation_uuids:
                recomendations.append(rec)

        primary_contact = subscription.get("primary_contact")
        context = {
            # Customer info
            "customer": customer,
            "customer_identifier": customer.get("identifier"),
            "customer_address": customer_address,
            # DHS contact info
            "DHS_contact": dhs_contact,
            # Subscription info
            "start_date": subscription.get("start_date"),
            "end_date": subscription.get("end_date"),
            "target_count": target_count,
            "cycles": cycles,
            "primary_contact": primary_contact,
            "primary_contact_email": primary_contact.get("email"),
            "subscription_stats": subscription_stats,
            "region_stats": region_stats,
            # Metrics
            "metrics": metrics,
            "yearly_report_start_date": yearly_start_date,
            "yearly_report_end_date": yearly_end_date,
            "cycles": sorted(cycles_stats, key=lambda cycle: cycle["start_date"],reverse=True),
            "percentage_trends_data": percentage_trends_data,
            "clickrate_vs_reportrate_data": clickrate_vs_reportrate_data,
            "trend": trend,
            "recommendations": recomendations,
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)
