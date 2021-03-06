"""Yearly Reports View."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.services import (
    CustomerService,
    DHSContactService,
    RecommendationService,
    SubscriptionService,
)
from reports.utils import (
    cycle_stats_to_click_rate_vs_report_rate,
    cycle_stats_to_percentage_trend_graph_data,
    determine_trend,
    format_timedelta,
    get_related_subscription_stats,
    get_relevant_recommendations,
    get_statistic_from_group,
    get_statistic_from_region_group,
    get_subscription_stats_for_yearly,
    get_template_details,
    get_yearly_start_dates,
    ratio_to_percent,
    set_cycle_quarters,
)

# GoPhish API Manager
campaign_manager = CampaignManager()
customer_service = CustomerService()
subscription_service = SubscriptionService()
dhs_contact_service = DHSContactService()
recommendation_service = RecommendationService()


class YearlyReportsView(APIView):
    """YearlyReportsView."""

    def get(self, request, **kwargs):
        """Get."""
        subscription_uuid = self.kwargs["subscription_uuid"]
        start_date_param = self.kwargs["start_date"]
        start_date = datetime.strptime(start_date_param, "%Y-%m-%dT%H:%M:%S.%f%z")
        subscription = subscription_service.get(subscription_uuid)
        customer = customer_service.get(subscription.get("customer_uuid"))

        dhs_contact = dhs_contact_service.get(subscription.get("dhs_contact_uuid"))

        cycles = subscription["cycles"]
        set_cycle_quarters(cycles)

        # target_count = sum([targets.get("stats").get("total") for targets in summary])
        # target_count = len(subscription["target_email_list"])

        yearly_start_date, yearly_end_date = get_yearly_start_dates(
            subscription, start_date
        )

        # Get subscription stats for the previous year.
        # Provide date values to get_subscription_stats_for_yearly for a different time span
        (
            subscription_stats,
            cycles_stats,
            total_targets_in_year,
        ) = get_subscription_stats_for_yearly(subscription)
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

        metrics = {
            "total_users_targeted": total_targets_in_year,
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

        _recomendations = recommendation_service.get_list()
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
            "target_count": total_targets_in_year,
            "primary_contact": primary_contact,
            "primary_contact_email": primary_contact.get("email"),
            "subscription_stats": subscription_stats,
            "region_stats": region_stats,
            # Metrics
            "metrics": metrics,
            "yearly_report_start_date": yearly_start_date,
            "yearly_report_end_date": yearly_end_date,
            "cycles": sorted(
                cycles_stats, key=lambda cycle: cycle["start_date"], reverse=True
            ),
            "percentage_trends_data": percentage_trends_data,
            "clickrate_vs_reportrate_data": clickrate_vs_reportrate_data,
            "trend": trend,
            "recommendations": recomendations,
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)
