"""
Reports Views.

This handles the api for all the Reports urls.
"""
# Standard Python Libraries
import datetime
import logging

# Third-Party Libraries
from django.conf import settings
from api.manager import CampaignManager
from api.models.dhs_models import DHSContactModel, validate_dhs_contact
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.models.template_models import (
    DeceptionLevelStatsModel,
    TemplateModel,
    validate_template,
)
from api.serializers.reports_serializers import (
    EmailReportsGetSerializer,
    ReportsGetSerializer,
)
from api.utils.db_utils import get_list, get_single, update_single
from django.http import FileResponse
from drf_yasg.utils import swagger_auto_schema
from notifications.views import ReportsEmailSender
from reports.utils import (
    campaign_templates_to_string,
    get_cycles_breakdown,
    get_most_successful_campaigns,
    get_related_subscription_stats,
    get_reports_to_click,
    get_statistic_from_group,
    get_subscription_stats_for_cycle,
    get_template_details,
    get_relevant_recommendations,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from api.utils.reports import download_pdf


logger = logging.getLogger(__name__)

# GoPhish API Manager
campaign_manager = CampaignManager()


class ReportsView(APIView):
    """
    This is the ReportsView API Endpoint.

    This handles the API a Get .
    """

    @swagger_auto_schema(
        responses={"200": ReportsGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Get Subscription Report data",
        operation_description="This fetches a subscription's report data by subscription uuid",
    )
    def get(self, request, subscription_uuid):
        """Get Method."""
        subscription_uuid = self.kwargs["subscription_uuid"]
        subscription = get_single(
            subscription_uuid, "subscription", SubscriptionModel, validate_subscription
        )

        campaigns = subscription.get("gophish_campaign_list")

        parameters = {
            "template_uuid": {"$in": subscription["templates_selected_uuid_list"]}
        }

        template_list = get_list(
            parameters, "template", TemplateModel, validate_template,
        )

        # boil it all down to a template name and a score in one object
        templates = {
            template.get("name"): template.get("deception_score")
            for template in template_list
        }

        # distribute statistics into deception levels
        levels = []
        levels.append(DeceptionLevelStatsModel("low", 1))
        levels.append(DeceptionLevelStatsModel("moderate", 2))
        levels.append(DeceptionLevelStatsModel("high", 3))

        for campaign in campaigns:
            level_number = campaign.get("deception_level")
            if level_number not in [1, 2, 3]:
                continue

            bucket = next(
                level for level in levels if level.level_number == level_number
            )
            bucket.sent = bucket.sent + campaign.get("phish_results", {}).get("sent", 0)
            bucket.clicked = bucket.clicked + campaign.get("phish_results", {}).get(
                "clicked", 0
            )
            bucket.opened = bucket.opened + campaign.get("phish_results", {}).get(
                "opened", 0
            )

        # aggregate statistics
        sent = sum(
            [campaign.get("phish_results", {}).get("sent", 0) for campaign in campaigns]
        )
        target_count = sum(
            [len(campaign.get("target_email_list")) for campaign in campaigns]
        )

        created_date = ""
        end_date = ""
        if campaigns:
            created_date = campaigns[0].get("created_date")
            end_date = campaigns[0].get("completed_date")

        start_date = subscription["start_date"]

        # Get statistics for the specified subscription during the specified cycle
        subscription_stats = get_subscription_stats_for_cycle(subscription, start_date)
        get_related_subscription_stats(subscription, start_date)
        get_cycles_breakdown(subscription["cycles"])

        # Get template details for each campaign template
        get_template_details(subscription_stats["campaign_results"])

        # Get recommendations for campaign
        recommendations = get_relevant_recommendations(subscription_stats)

        metrics = {
            "total_users_targeted": len(subscription["target_email_list"]),
            "number_of_email_sent_overall": get_statistic_from_group(
                subscription_stats, "stats_all", "sent", "count"
            ),
            "number_of_clicked_emails": get_statistic_from_group(
                subscription_stats, "stats_all", "clicked", "count"
            ),
            "number_of_opened_emails": get_statistic_from_group(
                subscription_stats, "stats_all", "opened", "count"
            ),
            "number_of_phished_users_overall": get_statistic_from_group(
                subscription_stats, "stats_all", "submitted", "count"
            ),
            "number_of_reports_to_helpdesk": get_statistic_from_group(
                subscription_stats, "stats_all", "reported", "count"
            ),
            "repots_to_clicks_ratio": get_reports_to_click(subscription_stats),
            "avg_time_to_first_click": get_statistic_from_group(
                subscription_stats, "stats_all", "clicked", "average"
            ),
            "avg_time_to_first_report": get_statistic_from_group(
                subscription_stats, "stats_all", "reported", "average"
            ),
            "most_successful_template": campaign_templates_to_string(
                get_most_successful_campaigns(subscription_stats, "reported")
            ),
        }

        context = {
            "customer_name": subscription.get("name"),
            "templates": templates,
            "start_date": created_date,
            "end_date": end_date,
            "levels": levels,
            "sent": sent,
            "target_count": target_count,
            "metrics": metrics,
            "recommendations": recommendations,
        }
        serializer = ReportsGetSerializer(context)
        return Response(serializer.data)


class MonthlyReportsEmailView(APIView):
    """
    This is the ReportsView Email API Endpoint.

    This handles the API a Get request for emailing a reports document
    """

    @swagger_auto_schema(
        responses={"200": EmailReportsGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Send Email Subscription Report PDF",
        operation_description="This sends a subscription report email by subscription uuid",
    )
    def get(self, request, subscription_uuid):
        """Get Method."""
        subscription = get_single(
            subscription_uuid, "subscription", SubscriptionModel, validate_subscription
        )
        message_type = "monthly_report"

        # Send email
        sender = ReportsEmailSender(subscription, message_type)
        sender.send()

        dhs_contact_uuid = subscription.get("dhs_contact_uuid")
        dhs_contact = get_single(
            dhs_contact_uuid, "dhs_contact", DHSContactModel, validate_dhs_contact
        )
        recipient_copy = dhs_contact.get("email") if dhs_contact else None

        subscription["email_report_history"].append(
            {
                "report_type": "Monthly",
                "sent": datetime.datetime.now(),
                "email_to": subscription.get("primary_contact").get("email"),
                "email_from": settings.SERVER_EMAIL,
                "bbc": recipient_copy,
                "manual": False,
            }
        )

        update_single(
            subscription_uuid,
            {"email_report_history": subscription["email_report_history"]},
            "subscription",
            SubscriptionModel,
            validate_subscription,
        )

        serializer = EmailReportsGetSerializer({"subscription_uuid": subscription_uuid})
        return Response(serializer.data)


class CycleReportsEmailView(APIView):
    """
    This is the ReportsView Email API Endpoint.

    This handles the API a Get request for emailing a reports document
    """

    @swagger_auto_schema(
        responses={"200": EmailReportsGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Send Email Subscription Report PDF",
        operation_description="This sends a subscription report email by subscription uuid",
    )
    def get(self, request, subscription_uuid):
        """Get Method."""
        subscription = get_single(
            subscription_uuid, "subscription", SubscriptionModel, validate_subscription
        )
        # message_type = "cycle_report"
        # Send email
        # sender = ReportsEmailSender(subscription, message_type)
        # sender.send()

        dhs_contact_uuid = subscription.get("dhs_contact_uuid")
        dhs_contact = get_single(
            dhs_contact_uuid, "dhs_contact", DHSContactModel, validate_dhs_contact
        )
        recipient_copy = dhs_contact.get("email") if dhs_contact else None

        subscription["email_report_history"].append(
            {
                "report_type": "Cycle",
                "sent": datetime.datetime.now(),
                "email_to": subscription.get("primary_contact").get("email"),
                "email_from": settings.SERVER_EMAIL,
                "bbc": recipient_copy,
                "manual": False,
            }
        )

        update_single(
            subscription_uuid,
            {"email_report_history": subscription["email_report_history"]},
            "subscription",
            SubscriptionModel,
            validate_subscription,
        )

        serializer = EmailReportsGetSerializer({"subscription_uuid": subscription_uuid})
        return Response(serializer.data)


class YearlyReportsEmailView(APIView):
    """
    This is the ReportsView Email API Endpoint.

    This handles the API a Get request for emailing a reports document
    """

    @swagger_auto_schema(
        responses={"200": EmailReportsGetSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Send Email Subscription Report PDF",
        operation_description="This sends a subscription report email by subscription uuid",
    )
    def get(self, request, subscription_uuid):
        """Get Method."""
        # subscription = get_single(
        #     subscription_uuid, "subscription", SubscriptionModel, validate_subscription
        # )
        # message_type = "yearly_report"
        # Send email
        # sender = ReportsEmailSender(subscription, message_type)
        # sender.send()
        # dhs_contact_uuid = subscription.get("dhs_contact_uuid")
        # dhs_contact = get_single(
        #     dhs_contact_uuid, "dhs_contact", DHSContactModel, validate_dhs_contact
        # )
        # recipient_copy = dhs_contact.get("email") if dhs_contact else None

        # subscription["email_report_history"].append({
        #        "report_type": "Annual Report",
        #        "sent": datetime.datetime.now(),
        #        "email_to": subscription.get("primary_contact").get("email"),
        #        "email_from": settings.SERVER_EMAIL,
        #        "bbc": recipient_copy,
        #        "manual": False,
        #    })

        # update_single(
        #    subscription_uuid,
        #    {"email_report_history": subscription["email_report_history"]},
        #    "subscription",
        #    SubscriptionModel,
        #    validate_subscription,
        # )

        serializer = EmailReportsGetSerializer({"subscription_uuid": subscription_uuid})
        return Response(serializer.data)


# These are as functions rather than classes, because extending the APIView class
# causes some issues when sending accept headers other than application/json
def monthly_reports_pdf_view(request, subscription_uuid, cycle):
    """Monthly_reports_pdf_view."""
    print(dir(request))
    print(request.headers)
    return FileResponse(
        download_pdf(
            "monthly",
            subscription_uuid,
            cycle,
            auth_header=request.headers.get("Authorization", None),
        ),
        as_attachment=True,
        filename="monthly_subscription_report.pdf",
    )


# These are as functions rather than classes, because extending the APIView class
# causes some issues when sending accept headers other than application/json
def cycle_reports_pdf_view(request, subscription_uuid, cycle):
    """Cycle_reports_pdf_view."""
    return FileResponse(
        download_pdf(
            "cycle",
            subscription_uuid,
            cycle,
            auth_header=request.headers.get("Authorization", None),
        ),
        as_attachment=True,
        filename="cycle_subscription_report.pdf",
    )


# These are as functions rather than classes, because extending the APIView class
# causes some issues when sending accept headers other than application/json
# which for this application/pdf is needed
def yearly_reports_pdf_view(request, subscription_uuid, cycle):
    """Yearly_reports_pdf_view."""
    return FileResponse(
        download_pdf(
            "yearly",
            subscription_uuid,
            cycle,
            auth_header=request.headers.get("Authorization", None),
        ),
        as_attachment=True,
        filename="yearly_subscription_report.pdf",
    )
