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
    campaign_templates_to_string,
    format_timedelta,
    get_closest_cycle_within_day_range,
    get_cycle_by_date_in_range,
    get_cycles_breakdown,
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


class YearlyReportsView(APIView):
    """
    Yearly Reports
    """

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
        summary = [
            campaign_manager.get("summary", campaign_id=campaign.get("campaign_id"))
            for campaign in campaigns
        ]
        target_count = sum([targets.get("stats").get("total") for targets in summary])

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

        context = {
            # Customer info
            "customer_name": customer.get("name"),
            "customer_identifier": customer.get("identifier"),
            "customer_address": customer_address,
            # DHS contact info
            "dhs_contact_name": dhs_contact_name,
            "dhs_contact_email": dhs_contact.get("email"),
            "dhs_contact_mobile_phone": dhs_contact.get("office_phone"),
            "dhs_contact_office_phone": dhs_contact.get("mobile_phone"),
            # Subscription info
            "start_date": subscription.get("start_date"),
            "end_date": subscription.get("end_date"),
            "target_count": target_count,
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)
