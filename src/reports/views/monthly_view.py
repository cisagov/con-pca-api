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
from api.utils.db_utils import get_list, get_single

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import TemplateView


# from . import views
from reports.utils import (
    get_subscription_stats_for_cycle,
    get_subscription_stats_for_month,
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
    pprintItem,
)

logger = logging.getLogger(__name__)

# GoPhish API Manager
campaign_manager = CampaignManager()


class MonthlyReportsView(APIView):
    """
    Monthly reports
    """

    def getMonthlyStats(self, subscription):
        start_date_param = self.kwargs["start_date"]
        target_report_date = datetime.strptime(
            start_date_param, "%Y-%m-%dT%H:%M:%S.%f%z"
        )

        # Get statistics for the specified subscription during the specified cycle

        subscription_stats = get_subscription_stats_for_month(
            subscription, target_report_date
        )

        active_cycle = get_cycle_by_date_in_range(subscription, target_report_date)
        active_campaigns = []
        for campaign in subscription["gophish_campaign_list"]:
            if campaign["campaign_id"] in active_cycle["campaigns_in_cycle"]:
                active_campaigns.append(campaign)

        target_count = 0
        for campaign in active_campaigns:
            target_count += len(campaign["target_email_list"])

        # subscription_stats = get_subscription_stats_for_cycle(
        #     subscription, start_date
        # )
        opened = get_statistic_from_group(
            subscription_stats, "stats_all", "opened", "count"
        )
        clicked = get_statistic_from_group(
            subscription_stats, "stats_all", "clicked", "count"
        )
        sent = get_statistic_from_group(
            subscription_stats, "stats_all", "sent", "count"
        )
        submitted = get_statistic_from_group(
            subscription_stats, "stats_all", "submitted", "count"
        )
        reported = get_statistic_from_group(
            subscription_stats, "stats_all", "reported", "count"
        )

        total = len(subscription["target_email_list"])
        low_mid_high_bar_data = get_stats_low_med_high_by_level(subscription_stats)
        zerodefault = [0] * 15
        low_mid_high_bar_data = (
            low_mid_high_bar_data if low_mid_high_bar_data is not None else zerodefault
        )

        metrics = {
            "total_users_targeted": total,
            "number_of_email_sent_overall": sent,
            "number_of_clicked_emails": clicked,
            "percent_of_clicked_emails": 0
            if sent == 0
            else round(float(clicked or 0) / float(1 if sent is None else sent), 2),
            "number_of_opened_emails": opened,
            "number_of_phished_users_overall": total,
            "percent_of_phished_users_overall": round(
                float(clicked or 0) / float(1 if total is None else total), 2
            ),
            "number_of_reports_to_helpdesk": reported,
            "percent_report_rate": 0
            if opened == 0
            else round(
                float(reported or 0) / float(1 if opened is None else opened), 2
            ),
            "reports_to_clicks_ratio": get_reports_to_click(subscription_stats),
            "avg_time_to_first_click": get_statistic_from_group(
                subscription_stats, "stats_all", "clicked", "average"
            ),
            "avg_time_to_first_report": get_statistic_from_group(
                subscription_stats, "stats_all", "reported", "average"
            ),
            "ratio_reports_to_clicks": 0
            if clicked == 0
            else round(
                float(reported or 0) / float(1 if clicked is None else clicked), 2
            ),
            "monthly_report_target_date": target_report_date,
            "target_count": target_count,
        }

        return metrics, subscription_stats

    def get(self, request, **kwargs):
        subscription_uuid = self.kwargs["subscription_uuid"]
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

        # target_count = campaign_manager.get("summary", campaign_id=campaign.get("campaign_id"))

        metrics, subscription_stats = self.getMonthlyStats(subscription)

        customer_address = """{},\n{}""".format(
            customer.get("address_1"), customer.get("address_2")
        )

        customer_address_2 = """{}, {} {} USA""".format(
            customer.get("city"), customer.get("state"), customer.get("zip_code"),
        )

        dhs_contact_name = "{} {}".format(
            dhs_contact.get("first_name"), dhs_contact.get("last_name")
        )

        primary_contact = subscription.get("primary_contact")
        primary_contact_name = "{} {}".format(
            primary_contact.get("first_name"), primary_contact.get("last_name")
        )

        total_users_targeted = len(subscription["target_email_list"])

        context = {
            # Customer info
            "customer_name": customer.get("name"),
            "customer_identifier": customer.get("identifier"),
            "customer_address": customer_address,
            "customer_address_2": customer_address_2,
            # primary contact info
            "primary_contact_name": primary_contact_name,
            "primary_contact_email": primary_contact.get("email"),
            # DHS contact info
            "dhs_contact_name": dhs_contact_name,
            "dhs_contact_email": dhs_contact.get("email"),
            "dhs_contact_mobile_phone": dhs_contact.get("office_phone"),
            "dhs_contact_office_phone": dhs_contact.get("mobile_phone"),
            # Subscription info
            "start_date": subscription.get("start_date"),
            "end_date": subscription.get("end_date"),
            "target_count": metrics["target_count"],
            "metrics": metrics,
            "subscription_stats": subscription_stats,
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)
