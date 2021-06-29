"""Yearly report views."""
# Standard Python Libraries
from datetime import timedelta

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
from api.utils.customer import format_customer_address
from api.utils.reports import download_pdf, is_nonhuman_request

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

        report_stats = get_yearly_stats(
            subscription, cycle, is_nonhuman_request(request)
        )
        region_stats = stats.get_related_customer_stats(customer)

        metrics = get_yearly_metrics(report_stats, region_stats)
        percentage_trends_data = stats.cycle_stats_to_percentage_trend_graph_data(
            report_stats["cycles"]
        )
        clickrate_vs_reportrate_data = stats.cycle_stats_to_click_rate_vs_report_rate(
            report_stats["cycles"]
        )
        trend = stats.determine_trend(report_stats["cycles"])

        context = {
            # Customer Info
            "customer": customer,
            "customer_identifier": customer["identifier"],
            "customer_address": format_customer_address(customer),
            # CISA Contact
            "DHS_contact": cisa_contact,
            # Subscription Info
            "start_date": subscription.get("start_date"),
            "end_date": subscription.get("end_date"),
            "cycles": sorted(
                report_stats["cycles"],
                key=lambda cycle: cycle["start_date"],
                reverse=True,
            ),
            # Primary Contact
            "primary_contact": subscription["primary_contact"],
            "primary_contact_email": subscription["primary_contact"]["email"],
            # Stats
            "target_count": report_stats["total_targets"],
            "subscription_stats": report_stats,
            "region_stats": region_stats,
            "metrics": metrics,
            "percentage_trends_data": percentage_trends_data,
            "clickrate_vs_reportrate_data": clickrate_vs_reportrate_data,
            "trend": trend,
            # Dates
            "yearly_report_start_date": report_stats["yearly_start"],
            "yearly_report_end_date": report_stats["yearly_end"],
            # TODO: Recommendations
            "recommendations": [],
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)


def email_view(request, subscription_uuid, cycle_uuid):
    """Email yearly report."""
    subscription = subscription_service.get(subscription_uuid)
    sender = EmailSender(
        subscription, "yearly_report", cycle_uuid, is_nonhuman_request(request)
    )
    sender.send()
    return JsonResponse(
        {"subscription_uuid": subscription_uuid}, status=status.HTTP_202_ACCEPTED
    )


def pdf_view(request, subscription_uuid, cycle_uuid):
    """Download yearly report."""
    return FileResponse(
        download_pdf(
            "yearly", subscription_uuid, cycle_uuid, is_nonhuman_request(request)
        ),
        as_attachment=True,
        filename="yearly_subscription_report.pdf",
    )


def get_yearly_stats(subscription, cycle, nonhuman=False):
    """Get statistics for yearly report."""
    yearly_start = cycle["start_date"] - timedelta(days=365)
    yearly_end = cycle["start_date"]
    yearly_cycles = stats.get_yearly_cycles(
        yearly_start, yearly_end, subscription["cycles"]
    )
    stats.set_cycle_year_increments(yearly_cycles)
    total_targets = 0

    campaign_stats = []
    for cycle in yearly_cycles:
        if cycle.get("phish_results_dirty"):
            stats.generate_cycle_phish_results(subscription, cycle)

        campaigns = stats.get_cycle_campaigns(
            cycle["cycle_uuid"], subscription["campaigns"]
        )
        total_targets += cycle["total_targets"]
        if cycle.get("override_total_reported", -1) > -1:
            stats.split_override_reports(
                cycle["override_total_reported"], campaigns, cycle["total_targets"]
            )

        cycle_campaign_stats = []
        for campaign in campaigns:
            template = template_service.get(campaign["template_uuid"])
            campaign_stat = stats.process_campaign(campaign, template, nonhuman)
            cycle_campaign_stats.append(campaign_stat)
            campaign_stats.append(campaign_stat)

        cycle_stat = stats.process_overall_stats(cycle_campaign_stats)
        stats.clean_stats(cycle_stat)
        cycle["cycle_stats"] = cycle_stat

    overall_stats = stats.process_overall_stats(campaign_stats)
    stats.clean_stats(overall_stats)
    overall_stats["campaign_results"] = campaign_stats
    overall_stats["total_targets"] = total_targets
    overall_stats["yearly_start"] = yearly_start
    overall_stats["yearly_end"] = yearly_end
    overall_stats["cycles"] = yearly_cycles
    return overall_stats


def get_yearly_metrics(yearly_stats, region_stats):
    """Get metrics for yearly report."""
    return {
        # Targets
        "total_users_targeted": yearly_stats["total_targets"],
        # Sent
        "number_of_email_sent_overall": yearly_stats["stats_all"]["sent"]["count"],
        # Opens
        "shortest_time_to_open": yearly_stats["stats_all"]["opened"]["minimum"],
        "median_time_to_open": yearly_stats["stats_all"]["opened"]["median"],
        "longest_time_to_open": yearly_stats["stats_all"]["opened"]["maximum"],
        # Reports
        "shortest_time_to_report": yearly_stats["stats_all"]["reported"]["minimum"],
        "median_time_to_report": yearly_stats["stats_all"]["reported"]["median"],
        # Regional Averages
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
    }
