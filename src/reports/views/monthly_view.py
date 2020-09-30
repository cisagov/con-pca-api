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
from django.utils import timezone
import pytz

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

    def getTemplateClickedIndicators(self, subscription_stats):
        key_vals = {
            "grammar": {"0": 0, "1": 0, "2": 0},
            "link_domain": {"0": 0, "1": 0},
            "logo_graphics": {"0": 0, "1": 0},
            "external": {"0": 0, "1": 0},
            "internal": {"0": 0, "1": 0, "2": 0},
            "authoritative": {"0": 0, "1": 0, "2": 0},
            "organization": {"0": 0, "1": 0},
            "public_news": {"0": 0, "1": 0},
            "curiosity": {"0": 0, "1": 0},
            "duty_obligation": {"0": 0, "1": 0},
            "fear": {"0": 0, "1": 0},
            "greed": {"0": 0, "1": 0},
        }

        for campaign in subscription_stats["campaign_results"]:
            if "clicked" in campaign["campaign_stats"]:
                apperance = campaign["template_details"]["appearance"]
                behavior = campaign["template_details"]["behavior"]
                relvancy = campaign["template_details"]["relevancy"]
                sender = campaign["template_details"]["sender"]
                all_identifiers = {**apperance, **behavior, **relvancy, **sender}
                for identifier in key_vals:
                    for val in key_vals[identifier].keys():
                        if all_identifiers[identifier] == int(val):
                            key_vals[identifier][val] += campaign["campaign_stats"][
                                "clicked"
                            ]["count"]

        subscription_stats["indicator_breakdown"] = key_vals
        self.__format_indicator_breakdown(subscription_stats)

    def __format_indicator_breakdown(self, subscription_stats):
        key_vals = {
            "grammar": {
                "name": "Apperance & Grammar",
                "0": "Poor",
                "1": "Decent",
                "2": "Proper",
            },
            "link_domain": {
                "name": "Link Domain",
                "0": "Fake",
                "1": "Spoofed / Hidden",
            },
            "logo_graphics": {
                "name": "Logo / Graphics",
                "0": "Fake / None",
                "1": "Sppofed / HTML",
            },
            "external": {"name": "Sender External", "0": "Fake / NA", "1": "Spoofed"},
            "internal": {
                "name": "Internal",
                "0": "Fake / NA",
                "1": "Unknown Spoofed",
                "2": "Known Spoofed",
            },
            "authoritative": {
                "name": "Authoritative",
                "0": "None",
                "1": "Corprate / Local",
                "2": "Federal / State",
            },
            "organization": {"name": "Relevancy Orginization", "0": "No", "1": "Yes"},
            "public_news": {"name": "Public News", "0": "No", "1": "Yes"},
            "curiosity": {"name": "Curiosity", "0": "Yes", "1": "No"},
            "duty_obligation": {"name": "Duty or Obligation", "0": "Yes", "1": "No"},
            "fear": {"name": "Fear", "0": "Yes", "1": "No"},
            "greed": {"name": "Greed", "0": "Yes", "1": "No"},
        }
        # Flatten out indicators
        flat_indicators = {}
        for indicator in subscription_stats["indicator_breakdown"]:
            for level in subscription_stats["indicator_breakdown"][indicator]:
                level_val = subscription_stats["indicator_breakdown"][indicator][level]
                flat_indicators[indicator + "-" + level] = level_val
        # Sort indicators
        sorted_flat_indicators = sorted(flat_indicators.items(), key=lambda kv: kv[1])
        # Get proper name and format output
        indicator_formatted = []
        rank = 0
        previous_val = None
        for indicator in sorted_flat_indicators:
            key_and_level = indicator[0].split("-")
            key = key_and_level[0]
            level = key_and_level[1]
            formated_val = indicator[1]
            formated_name = key_vals[key]["name"]
            formated_level = key_vals[key][level]
            if previous_val is None:
                previous_val = formated_val
            else:
                if previous_val != formated_val:
                    rank += 1
                previous_val = formated_val
            percent = 0
            if subscription_stats["stats_all"]["clicked"]["count"] > 0:
                percent = (
                    formated_val / subscription_stats["stats_all"]["clicked"]["count"]
                )
            indicator_formatted.insert(
                0,
                {
                    "name": formated_name,
                    "level": formated_level,
                    "value": formated_val,
                    "percent": percent,
                    "rank": rank,
                },
            )
        subscription_stats["indicator_ranking"] = indicator_formatted

    def getMonthlyStats(self, subscription):
        start_date_param = self.kwargs["start_date"]
        target_report_date = datetime.strptime(
            start_date_param, "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        cycle_uuid = None
        if "cycle_uuid" in self.kwargs:
            cycle_uuid = self.kwargs["cycle_uuid"]

        # Get statistics for the specified subscription during the specified cycle

        subscription_stats = get_subscription_stats_for_month(
            subscription, target_report_date, cycle_uuid
        )
        get_template_details(subscription_stats["campaign_results"])
        self.getTemplateClickedIndicators(subscription_stats)

        # Get the correct cycle based on the provided start_date
        if cycle_uuid:
            active_cycle = subscription["cycles"][0]
            for cycle in subscription["cycles"]:
                if cycle["cycle_uuid"] == cycle_uuid:
                    active_cycle = cycle
        else:
            active_cycle = get_cycle_by_date_in_range(subscription, end_date)

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

        display_end_date = active_cycle["end_date"]
        date_now = datetime.now()
        if not timezone.is_aware(date_now):
            utc = pytz.UTC
            date_now = utc.localize(date_now)
        if not timezone.is_aware(display_end_date):
            utc = pytz.UTC
            display_end_date = utc.localize(display_end_date)
        if display_end_date > date_now:
            display_end_date = date_now

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
            "start_date": active_cycle["start_date"],
            "end_date": display_end_date,
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
