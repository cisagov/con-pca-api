"""
API URLs.

This lists all urls under the API app.
"""
# Third-Party Libraries
from django.urls import path

# cisagov Libraries
from api.views import (
    customer_views,
    cycle_views,
    dhs_views,
    image_views,
    landing_page_views,
    recommendations_views,
    sendingprofile_views,
    subscription_views,
    tag_views,
    template_views,
    user_views,
    webhook_views,
)
from api.views.reports import (
    cycle_report_views,
    monthly_report_views,
    stats_page_views,
    system_report_views,
    yearly_report_views,
)

urlpatterns = [
    # Subscription
    path(
        "v1/subscriptions/",
        subscription_views.SubscriptionsListView.as_view(),
        name="subscriptions_list_api",
    ),
    path(
        "v1/subscriptions/valid/",
        subscription_views.SubscriptionValidView.as_view(),
        name="subscription_valid_api",
    ),
    path(
        "v1/subscription/<subscription_uuid>/",
        subscription_views.SubscriptionView.as_view(),
        name="subscriptions_get_api",
    ),
    path(
        "v1/subscription/customer/<customer_uuid>/",
        subscription_views.SubscriptionsCustomerListView.as_view(),
        name="subscriptions_customer_get_api",
    ),
    path(
        "v1/subscription/template/<template_uuid>/",
        subscription_views.SubscriptionsTemplateListView.as_view(),
        name="subscriptions_template_get_api",
    ),
    path(
        "v1/subscription/stop/<subscription_uuid>/",
        subscription_views.SubscriptionStopView.as_view(),
        name="subscription_stop_api",
    ),
    path(
        "v1/subscription/restart/<subscription_uuid>/",
        subscription_views.SubscriptionRestartView.as_view(),
        name="subscription_restart_api",
    ),
    path(
        "v1/subscription/targetcache/<subscription_uuid>/",
        subscription_views.SubscriptionTargetCacheView.as_view(),
        name="subscription_update_target_cache_api",
    ),
    # API Reports
    path(
        "v1/reports/<subscription_uuid>/monthly/<cycle_uuid>/",
        monthly_report_views.ReportView.as_view(),
        name="reports_monthly_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/cycle/<cycle_uuid>/",
        cycle_report_views.ReportView.as_view(),
        name="reports_cycle_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/yearly/<cycle_uuid>/",
        yearly_report_views.ReportView.as_view(),
        name="reports_yearly_api",
    ),
    # Stats Page
    path(
        "v1/reports/<subscription_uuid>/subscription-stats-page/<cycle_uuid>/",
        stats_page_views.CycleStatusView.as_view(),
        name="stats_page_view_api",
    ),
    # Aggregate Page
    path(
        "v1/reports/aggregate/",
        system_report_views.SystemReportsView.as_view(),
        name="system_reports_page",
    ),
    # Report Emails Sent
    path(
        "v1/reports/subscription_report_emails_sent/<subscription_uuid>/",
        system_report_views.SubsriptionReportsListView.as_view(),
        name="system_reports_page",
    ),
    # PDF Reports
    path(
        "v1/reports/<subscription_uuid>/pdf/monthly/<cycle_uuid>/",
        monthly_report_views.pdf_view,
        name="reports_pdf_monthly_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/pdf/cycle/<cycle_uuid>/",
        cycle_report_views.pdf_view,
        name="reports_pdf_cycle_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/pdf/yearly/<cycle_uuid>/",
        yearly_report_views.pdf_view,
        name="reports_pdf_yearly_api",
    ),
    # Email Reports
    path(
        "v1/reports/<subscription_uuid>/email/monthly/<cycle_uuid>/",
        monthly_report_views.email_view,
        name="reports_email_monthly_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/email/cycle/<cycle_uuid>/",
        cycle_report_views.email_view,
        name="reports_email_cycle_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/email/yearly/<cycle_uuid>/",
        yearly_report_views.email_view,
        name="reports_email_yearly_api",
    ),
    # Templates
    path(
        "v1/templates/",
        template_views.TemplatesListView.as_view(),
        name="templates_list_api",
    ),
    path(
        "v1/templates/import/",
        template_views.TemplateEmailImportView.as_view(),
        name="template_import_api",
    ),
    path(
        "v1/template/<template_uuid>/",
        template_views.TemplateView.as_view(),
        name="template_get_api",
    ),
    path(
        "v1/template/stop/<template_uuid>/",
        template_views.TemplateStopView.as_view(),
        name="template_stop_api",
    ),
    # Tags
    path(
        "v1/tags/",
        tag_views.TagsView.as_view(),
        name="tags_list_api",
    ),
    path(
        "v1/tag/<tag_uuid>/",
        tag_views.TagView.as_view(),
        name="tags_get_api",
    ),
    # Customers
    path(
        "v1/customers/",
        customer_views.CustomerListView.as_view(),
        name="customer_list_api",
    ),
    path(
        "v1/customer/<customer_uuid>/",
        customer_views.CustomerView.as_view(),
        name="customer_get_api",
    ),
    # Sending Profiles
    path(
        "v1/sendingprofiles/",
        sendingprofile_views.SendingProfilesListView.as_view(),
        name="sendingprofile_list_api",
    ),
    path(
        "v1/sendingprofile/<id>/",
        sendingprofile_views.SendingProfileView.as_view(),
        name="sendingprofile_get_api",
    ),
    # Webhooks
    path(
        "v1/inboundwebhook/",
        webhook_views.IncomingWebhookView.as_view(),
        name="inbound_webhook_api",
    ),
    # Images
    path(
        "v1/imageupload/",
        image_views.ImageView.as_view(),
        name="image_upload",
    ),
    # Sector Industry
    path(
        "v1/sectorindustry/",
        customer_views.SectorIndustryView.as_view(),
        name="sector_industry_list",
    ),
    # CISA Contacts
    path(
        "v1/dhscontacts/",
        dhs_views.DHSContactListView.as_view(),
        name="dhs_contact_list",
    ),
    path(
        "v1/dhscontact/<dhs_contact_uuid>/",
        dhs_views.DHSContactView.as_view(),
        name="dhs_contact_get_api",
    ),
    # Recommendations
    path(
        "v1/recommendations/",
        recommendations_views.RecommendationsListView.as_view(),
        name="recommendations_list",
    ),
    path(
        "v1/recommendations/<recommendations_uuid>/",
        recommendations_views.RecommendationsView.as_view(),
        name="recommendations_get_api",
    ),
    # Email Reported
    path(
        "v1/cycleemailreported/<subscription_uuid>/",
        cycle_views.CycleReportedView.as_view(),
        name="cycle_email_report_api",
    ),
    # Landing Pages
    path(
        "v1/landingpages/",
        landing_page_views.LandingPagesListView.as_view(),
        name="landing_page_list_api",
    ),
    path(
        "v1/landingpages/<with_default>/",
        landing_page_views.LandingPagesListView.as_view(),
        name="landing_page_list_api",
    ),
    path(
        "v1/landingpage/<landing_page_uuid>/",
        landing_page_views.LandingPageView.as_view(),
        name="landing_page_get_api",
    ),
    # Test EMail
    path(
        "v1/test_email/",
        template_views.SendingTestEmailsView.as_view(),
        name="test_email_api",
    ),
    # Users
    path(
        "v1/users/",
        user_views.UsersView.as_view(),
        name="users_view_api",
    ),
    path(
        "v1/user/<username>/",
        user_views.UserView.as_view(),
        name="user_view_api",
    ),
    path(
        "v1/user/<username>/confirm/",
        user_views.UserConfirmView.as_view(),
        name="user_confirm_view_api",
    ),
]
