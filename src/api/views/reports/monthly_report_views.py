"""Views for monthly status report."""
# Third-Party Libraries
from django.http import FileResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.notifications import EmailSender
from api.services import (
    CustomerService,
    DHSContactService,
    SubscriptionService,
    TemplateService,
)
from api.utils import stats
from api.utils.contact import format_contact_name
from api.utils.customer import format_customer_address_1, format_customer_address_2
from api.utils.generic import display_date
from api.utils.reports.pdf import download_pdf

subscription_service = SubscriptionService()
customer_service = CustomerService()
dhs_contact_service = DHSContactService()
template_service = TemplateService()


class ReportView(APIView):
    """ReportView."""

    def get(self, request, subscription_uuid, cycle_uuid):
        """Get."""
        subscription = subscription_service.get(subscription_uuid)
        cycle = stats.get_subscription_cycle(subscription, cycle_uuid)
        customer = customer_service.get(subscription["customer_uuid"])
        cisa_contact = dhs_contact_service.get(subscription["dhs_contact_uuid"])
        report_stats = get_monthly_stats(subscription, cycle)
        metrics = get_monthly_metrics(cycle, report_stats)

        context = {
            # Customer Info
            "customer_name": customer["name"],
            "customer_identifier": customer["identifier"],
            "customer_address": format_customer_address_1(customer),
            "customer_address_2": format_customer_address_2(customer),
            # Primary Contact Info
            "primary_contact_name": format_contact_name(
                subscription["primary_contact"]
            ),
            "primary_contact_email": subscription["primary_contact"]["email"],
            # CISA Contact Info
            "dhs_contact_name": format_contact_name(cisa_contact),
            "dhs_contact_email": cisa_contact["email"],
            "dhs_contact_mobile_phone": cisa_contact.get("mobile_phone"),
            "dhs_contact_office_phone": cisa_contact.get("office_phone"),
            # Subscription Info
            "start_date": subscription.get("start_date"),
            "end_date": subscription.get("end_date"),
            "target_count": metrics["target_count"],  # Get From metrics
            "metrics": metrics,  # Metrics
            "subscription_stats": report_stats,  # Stats
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)


def email_view(request, subscription_uuid, cycle_uuid):
    """Email monthly report."""
    subscription = subscription_service.get(subscription_uuid)
    sender = EmailSender(subscription, "monthly_report", cycle_uuid)
    sender.send()
    return JsonResponse(
        {"subscription_uuid": subscription_uuid}, status=status.HTTP_202_ACCEPTED
    )


def pdf_view(request, subscription_uuid, cycle_uuid):
    """Download monthly report."""
    return FileResponse(
        download_pdf("monthly", subscription_uuid, cycle_uuid),
        as_attachment=True,
        filename="monthly_subscription_report.pdf",
    )


def get_monthly_stats(subscription, cycle):
    """Get statistics for monthly report."""
    campaigns = stats.get_cycle_campaigns(
        cycle["cycle_uuid"], subscription["campaigns"]
    )

    if cycle.get("override_total_reported", -1) > -1:
        stats.split_override_reports(
            cycle["override_total_reported"], campaigns, cycle["total_targets"]
        )

    campaign_stats = []
    for campaign in campaigns:
        template = template_service.get(campaign["template_uuid"])
        campaign_stats.append(stats.process_campaign(campaign, template))
    overall_stats = stats.process_overall_stats(campaign_stats)
    stats.clean_stats(overall_stats)
    return overall_stats


def get_monthly_metrics(cycle, monthly_stats):
    """Get metrics for monthly report."""
    return {
        # Targets
        "target_count": cycle["total_targets"],
        "total_users_targeted": cycle["total_targets"],
        # Sent
        "number_of_emails_sent_overall": monthly_stats["stats_all"]["sent"]["count"],
        # Clicked
        "number_of_clicked_emails": monthly_stats["stats_all"]["clicked"]["count"],
        "percent_of_clicked_emails": stats.ratio_to_percent(
            stats.get_ratio(
                monthly_stats["stats_all"]["clicked"]["count"],
                monthly_stats["stats_all"]["sent"]["count"],
            )
        ),
        "avg_time_to_first_click": monthly_stats["stats_all"]["clicked"]["average"],
        # Opened
        "number_of_opened_emails": monthly_stats["stats_all"]["opened"]["count"],
        # Phished Users
        "number_of_phished_users_overall": cycle["total_targets"],
        "percent_of_phished_users_overall": stats.ratio_to_percent(
            stats.get_ratio(
                monthly_stats["stats_all"]["clicked"]["count"],
                cycle["total_targets"],
            )
        ),
        # Reports
        "number_of_reports_to_helpdesk": monthly_stats["stats_all"]["reported"][
            "count"
        ],
        "percent_report_rate": stats.ratio_to_percent(
            stats.get_ratio(
                monthly_stats["stats_all"]["reported"]["count"],
                monthly_stats["stats_all"]["sent"]["count"],
            )
        ),
        "reports_to_clicks_ratio": stats.get_ratio(
            monthly_stats["stats_all"]["reported"]["count"],
            monthly_stats["stats_all"]["clicked"]["count"],
        ),
        "avg_time_to_first_report": monthly_stats["stats_all"]["reported"]["average"],
        "ratio_reports_to_clicks": stats.get_ratio(
            monthly_stats["stats_all"]["reported"]["count"],
            monthly_stats["stats_all"]["clicked"]["count"],
        ),
        # Other Info
        "start_date": cycle["start_date"],
        "end_date": display_date(cycle["end_date"]),
    }
