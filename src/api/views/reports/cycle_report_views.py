"""Cycle report views."""
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
from api.utils.customer import get_company
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
        stats.set_cycle_year_increments(subscription["cycles"])
        cycle = stats.get_subscription_cycle(subscription, cycle_uuid)
        customer = customer_service.get(subscription["customer_uuid"])
        cisa_contact = dhs_contact_service.get(subscription["dhs_contact_uuid"])
        report_stats = get_cycle_stats(subscription, cycle)
        previous_cycle_stats = stats.get_simple_stats_from_subscription(subscription)
        region_stats = stats.get_related_customer_stats(customer)

        metrics = get_cycle_metrics(cycle, report_stats, region_stats)

        context = {
            # Subscription Info
            "subscription_uuid": subscription_uuid,
            # Cycle Info
            "target_cycle": cycle,
            "dates": {
                "start": cycle["start_date"],
                "end": cycle["end_date"],
            },
            "cycles": subscription["cycles"],
            # Primary Contact Info
            "subscription_primary_contact": subscription["primary_contact"],
            "primary_contact": subscription["primary_contact"],
            "primary_contact_email": subscription["primary_contact"]["email"],
            # Customer Info
            "company": get_company(customer),
            "customer": customer,
            # CISA Contact Info
            "DHS_contact": cisa_contact,
            "dhs_contact_name": format_contact_name(cisa_contact),
            "dhs_contact_email": cisa_contact["email"],
            # Stats
            "previous_cycles": previous_cycle_stats,
            "metrics": metrics,
            "subscription_stats": report_stats,
            "region_stats": region_stats,
            "click_time_vs_report_time": stats.click_time_vs_report_time(
                report_stats["campaign_results"]
            ),
            # Templates
            "templates_by_group": stats.group_campaigns_by_deception_level(
                report_stats["campaign_results"]
            ),
            # TODO: Recommendations
            "recommendations": [],
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)


def email_view(request, subscription_uuid, cycle_uuid):
    """Email cycle report."""
    subscription = subscription_service.get(subscription_uuid)
    sender = EmailSender(subscription, "cycle_report", cycle_uuid)
    sender.send()
    return JsonResponse(
        {"subscription_uuid": subscription_uuid}, status=status.HTTP_202_ACCEPTED
    )


def pdf_view(request, subscription_uuid, cycle_uuid):
    """Download cycle reprot."""
    return FileResponse(
        download_pdf(
            "cycle",
            subscription_uuid,
            cycle_uuid,
        ),
        as_attachment=True,
        filename="cycle_subscription_report.pdf",
    )


def get_cycle_stats(subscription, cycle):
    """Get cycle statistics."""
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
    overall_stats["campaign_results"] = campaign_stats
    return overall_stats


def get_cycle_metrics(cycle, cycle_stats, region_stats):
    """Get cycle metrics."""
    return {
        # Targets
        "total_users_targeted": cycle["total_targets"],
        # Sent
        "emails_sent_over_target_count": round(
            cycle_stats["stats_all"]["sent"]["count"] / cycle["total_targets"], 2
        ),
        "number_of_emails_sent_overall": cycle_stats["stats_all"]["sent"]["count"],
        "percent_of_phished_users": stats.ratio_to_percent(
            stats.get_ratio(
                cycle_stats["stats_all"]["sent"]["count"],
                cycle["total_targets"],
            )
        ),
        # Clicked
        "avg_time_to_first_click": cycle_stats["stats_all"]["clicked"]["average"],
        "median_time_to_first_click": cycle_stats["stats_all"]["clicked"]["median"],
        "number_of_clicked_emails": cycle_stats["stats_all"]["clicked"]["count"],
        "percent_of_clicked_emails": stats.ratio_to_percent(
            stats.get_ratio(
                cycle_stats["stats_all"]["clicked"]["count"],
                cycle_stats["stats_all"]["sent"]["count"],
            )
        ),
        # Opened
        "number_of_opened_emails": cycle_stats["stats_all"]["opened"]["count"],
        "shortest_time_to_open": cycle_stats["stats_all"]["opened"]["minimum"],
        "median_time_to_open": cycle_stats["stats_all"]["opened"]["median"],
        "longest_time_to_open": cycle_stats["stats_all"]["opened"]["maximum"],
        # Reports
        "avg_time_to_first_report": cycle_stats["stats_all"]["reported"]["average"],
        "number_of_reports_to_helpdesk": cycle_stats["stats_all"]["reported"]["count"],
        "percent_report_rate": stats.ratio_to_percent(
            stats.get_ratio(
                cycle_stats["stats_all"]["reported"]["count"],
                cycle_stats["stats_all"]["sent"]["count"],
            )
        ),
        "reports_to_clicks_ratio": stats.get_ratio(
            cycle_stats["stats_all"]["reported"]["count"],
            cycle_stats["stats_all"]["clicked"]["count"],
        ),
        "shortest_time_to_report": cycle_stats["stats_all"]["reported"]["minimum"],
        "median_time_to_report": cycle_stats["stats_all"]["reported"]["median"],
        # Phished Users
        "number_of_phished_users_overall": cycle["total_targets"],
        # Customer Stats
        "customer_clicked_avg": stats.ratio_to_percent(
            region_stats["customer"]["clicked_ratio"]
        ),
        "national_clicked_avg": stats.ratio_to_percent(
            region_stats["national"]["clicked_ratio"]
        ),
        "industry_clicked_avg": stats.ratio_to_percent(
            region_stats["industry"]["clicked_ratio"]
        ),
        "sector_clicked_avg": stats.ratio_to_percent(
            region_stats["sector"]["clicked_ratio"]
        ),
        # Template
        "most_successful_template": stats.campaign_templates_to_string(
            stats.get_most_successful_campaigns(
                cycle_stats["campaign_results"], "clicked"
            )
        ),
    }
