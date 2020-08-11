"""
API URLs.

This lists all urls under the API app.
"""
# Third-Party Libraries
from api.views import (
    campaign_views,
    customer_views,
    cycle_views,
    dhs_views,
    image_views,
    recommendations_views,
    report_views,
    sendingprofile_views,
    subscription_views,
    template_views,
    webhook_views,
    landing_page_views,
)
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Con-PCA API",
        default_version="v1",
        description="""This is the API documentation for Con-PCA.
        This was created to define all API calls and repsonses.""",
        terms_of_service="https://github.com/cisagov/cpa/blob/develop/LICENSE",
        contact=openapi.Contact(email="peter.mercado255@gmail.com"),
        license=openapi.License(name="Public Domain"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url="http://localhost:8000",
)

urlpatterns = [
    path(
        "v1/swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "v1/swagger.yaml", schema_view.without_ui(cache_timeout=0), name="schema-yaml"
    ),
    path(
        "v1/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "v1/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    path(
        "v1/subscriptions/",
        subscription_views.SubscriptionsListView.as_view(),
        name="subscriptions_list_api",
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
        "v1/reports/<subscription_uuid>/",
        report_views.ReportsView.as_view(),
        name="reports_get_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/pdf/monthly/<cycle>/",
        report_views.monthly_reports_pdf_view,
        name="reports_get_pdf_monthly_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/pdf/cycle/<cycle>/",
        report_views.cycle_reports_pdf_view,
        name="reports_get_pdf_cycle_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/pdf/yearly/<cycle>/",
        report_views.yearly_reports_pdf_view,
        name="reports_get_pdf_yearly_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/email/monthly/",
        report_views.MonthlyReportsEmailView.as_view(),
        name="reports_get_pdf_monthly_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/email/cycle/",
        report_views.CycleReportsEmailView.as_view(),
        name="reports_get_pdf_cycle_api",
    ),
    path(
        "v1/reports/<subscription_uuid>/email/yearly/",
        report_views.YearlyReportsEmailView.as_view(),
        name="reports_get_pdf_yearly_api",
    ),
    path(
        "v1/templates/",
        template_views.TemplatesListView.as_view(),
        name="templates_list_api",
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
    path("v1/tags/", template_views.TagsView.as_view(), name="tags_list_api",),
    path("v1/tag/<tag_uuid>/", template_views.TagView.as_view(), name="tags_get_api",),
    path(
        "v1/campaigns/", campaign_views.CampaignListView.as_view(), name="campaign_list"
    ),
    path(
        "v1/campaign/<campaign_id>/",
        campaign_views.CampaignDetailView.as_view(),
        name="campaign_detail",
    ),
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
    path(
        "v1/inboundwebhook/",
        webhook_views.IncomingWebhookView.as_view(),
        name="inbound_webhook_api",
    ),
    path("v1/imageupload/", image_views.ImageView.as_view(), name="image_upload",),
    path(
        "v1/sectorindustry/",
        customer_views.SectorIndustryView.as_view(),
        name="sector_industry_list",
    ),
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
    path(
        "v1/cycleemailreported/<subscription_uuid>/",
        cycle_views.CycleReportedView.as_view(),
        name="cycle_email_report_api",
    ),
    path(
        "v1/landingpages/",
        landing_page_views.LandingPagesListView.as_view(),
        name="landing_page_list_api",
    ),
    path(
        "v1/landingpage/<landing_page_uuid>/",
        landing_page_views.LandingPageView.as_view(),
        name="landing_page_get_api",
    ),
    path(
        "v1/landingpage/stop/<landing_page_uuid>/",
        landing_page_views.LandingPageStopView.as_view(),
        name="landing_page_stop_api",
    ),
]
