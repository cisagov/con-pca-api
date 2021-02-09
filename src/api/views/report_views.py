"""Reports Views."""
# Third-Party Libraries
from django.http import FileResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from schematics.types import IntType, StringType

# cisagov Libraries
from api.manager import CampaignManager
from api.notifications import EmailSender
from api.serializers.reports_serializers import (
    EmailReportsGetSerializer,
    ReportsGetSerializer,
)
from api.services import SubscriptionService, TemplateService
from api.utils.reports import download_pdf
from reports.utils import (
    campaign_templates_to_string,
    get_cycles_breakdown,
    get_most_successful_campaigns,
    get_related_subscription_stats,
    get_relevant_recommendations,
    get_reports_to_click,
    get_statistic_from_group,
    get_subscription_stats_for_cycle,
    get_template_details,
)

# database services
template_service = TemplateService()
subscription_service = SubscriptionService()

# GoPhish API Manager
campaign_manager = CampaignManager()


class DeceptionLevelStatsModel:
    """DeceptionLevelStatsModel."""

    level = StringType()
    level_number = IntType()
    sent = IntType()
    total = IntType()
    opened = IntType()
    clicked = IntType()
    submitted_data = IntType()
    email_reported = IntType()

    def __init__(self, level, level_number):
        """Create Model."""
        self.level = level
        self.level_number = level_number
        self.sent = 0
        self.total = 0
        self.opened = 0
        self.clicked = 0
        self.submitted_data = 0
        self.email_reported = 0


class ReportsView(APIView):
    """ReportsView."""

    def get(self, request, subscription_uuid):
        """Get."""
        subscription_uuid = self.kwargs["subscription_uuid"]
        subscription = subscription_service.get(subscription_uuid)

        campaigns = subscription.get("campaigns")

        parameters = {
            "template_uuid": {"$in": subscription["templates_selected_uuid_list"]}
        }

        template_list = template_service.get_list(parameters)

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
        subscription_stats, _ = get_subscription_stats_for_cycle(
            subscription, cycle_uuid=None, start_date=start_date
        )
        get_related_subscription_stats(subscription, start_date)
        get_cycles_breakdown(subscription["cycles"])

        # Get template details for each campaign template
        get_template_details(subscription_stats["campaign_results"])

        # Get recommendations for campaign
        recommendations = get_relevant_recommendations(subscription_stats)

        metrics = {
            "total_users_targeted": target_count,
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


def monthly_report_email_view(request, subscription_uuid, cycle, cycle_uuid=None):
    """Email monthly report."""
    subscription = subscription_service.get(subscription_uuid)
    sender = EmailSender(subscription, "monthly_report", cycle, cycle_uuid)
    sender.send()
    serializer = EmailReportsGetSerializer({"subscription_uuid": subscription_uuid})
    return JsonResponse(serializer.data)


def monthly_reports_pdf_view(request, subscription_uuid, cycle, cycle_uuid=None):
    """Download monthly report."""
    return FileResponse(
        download_pdf("monthly", subscription_uuid, cycle, cycle_uuid),
        as_attachment=True,
        filename="monthly_subscription_report.pdf",
    )


def cycle_report_email_view(request, subscription_uuid, cycle):
    """Email cycle report."""
    subscription = subscription_service.get(subscription_uuid)
    sender = EmailSender(subscription, "cycle_report", cycle)
    sender.send()
    serializer = EmailReportsGetSerializer({"subscription_uuid": subscription_uuid})
    return JsonResponse(serializer.data)


def cycle_reports_pdf_view(request, subscription_uuid, cycle):
    """Download cycle reprot."""
    return FileResponse(
        download_pdf(
            "cycle",
            subscription_uuid,
            cycle,
        ),
        as_attachment=True,
        filename="cycle_subscription_report.pdf",
    )


def yearly_report_email_view(request, subscription_uuid, cycle):
    """Email yearly report."""
    subscription = subscription_service.get(subscription_uuid)
    sender = EmailSender(subscription, "yearly_report", cycle)
    sender.send()
    serializer = EmailReportsGetSerializer({"subscription_uuid": subscription_uuid})
    return JsonResponse(serializer.data)


def yearly_reports_pdf_view(request, subscription_uuid, cycle):
    """Download yearly report."""
    return FileResponse(
        download_pdf(
            "yearly",
            subscription_uuid,
            cycle,
        ),
        as_attachment=True,
        filename="yearly_subscription_report.pdf",
    )
