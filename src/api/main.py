"""Domain manager."""
# Standard Python Libraries
from datetime import date
from logging import INFO, basicConfig
from types import FunctionType, MethodType

# Third-Party Libraries
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template
from flask.json import JSONEncoder
from marshmallow.exceptions import ValidationError

# cisagov Libraries
from api.app import app
from api.commands.load_test_data import load_test_data
from api.config.environment import (
    EMAIL_MINUTES,
    FAILED_EMAIL_MINUTES,
    REDIS_HOST,
    REDIS_PORT,
    TASK_MINUTES,
    TESTING,
)
from api.initialize import initialization_tasks
from api.phish import emails_job
from api.tasks import failed_emails_job, tasks_job
from api.views.about_views import AboutView
from api.views.auth_views import (
    LoginView,
    RefreshTokenView,
    RegisterView,
    ResetPasswordView,
)
from api.views.config_views import ConfigView
from api.views.customer_views import (
    ArchiveCustomerView,
    CustomerCountView,
    CustomersPagedView,
    CustomersPOCView,
    CustomersView,
    CustomerView,
    SectorIndustryView,
)
from api.views.cycle_views import (
    CycleManualReportsView,
    CycleStatsView,
    CyclesView,
    CycleView,
)
from api.views.db_views import DatabaseManagementView
from api.views.failed_email_views import FailedEmailsView, FailedEmailView
from api.views.landing_page_views import (
    LandingPagesView,
    LandingPageTemplatesView,
    LandingPageView,
)
from api.views.logging_views import LoggingView
from api.views.nonhuman_views import NonHumansView
from api.views.notification_views import (
    NotificationDuplicateView,
    NotificationImportView,
    NotificationsView,
    NotificationView,
)
from api.views.recommendation_views import RecommendationsView, RecommendationView
from api.views.report_views import (
    AggregateReportView,
    OverdueTasksReportView,
    ReportEmailView,
    ReportGoEmailView,
    ReportGoPdfView,
    ReportHtmlView,
    ReportPdfView,
)
from api.views.sending_profile_views import SendingProfilesView, SendingProfileView
from api.views.subscription_views import (
    SubscriptionCountView,
    SubscriptionCurrentTemplatesView,
    SubscriptionHeaderView,
    SubscriptionLaunchView,
    SubscriptionNextTemplatesView,
    SubscriptionResetProcessingStateView,
    SubscriptionSafelistExportView,
    SubscriptionSafelistSendView,
    SubscriptionsPagedView,
    SubscriptionsStatusView,
    SubscriptionsView,
    SubscriptionTestView,
    SubscriptionValidView,
    SubscriptionView,
)
from api.views.tag_views import TagsView
from api.views.template_views import (
    TemplateDuplicateView,
    TemplateImportView,
    TemplatesSelectView,
    TemplatesView,
    TemplateView,
)
from api.views.user_views import UserConfirmView, UsersView, UserView
from api.views.utility_views import ImageEncodeView, RandomPasswordView, TestEmailView
from utils.decorators.auth import auth_required
from utils.logging import setLogger

# register apps
url_prefix = "/api"

rules = [
    # About Views
    ("/about/", AboutView),
    # Config Views
    ("/config/", ConfigView),
    # Customer Views
    ("/customers/", CustomersView),
    ("/customers/contacts/", CustomersPOCView),
    ("/customer/<customer_id>/", CustomerView),
    ("/customer/count/", CustomerCountView),
    ("/customerPaged/", CustomersPagedView),
    (
        "/customerPaged/<page>/<pagesize>/<sortby>/<sortorder>/",
        CustomersPagedView,
    ),
    ("/archivecustomer/<customer_id>/", ArchiveCustomerView),
    # Cycle Views
    ("/cycles/", CyclesView),
    ("/cycle/<cycle_id>/", CycleView),
    ("/cycle/<cycle_id>/manual_reports/", CycleManualReportsView),
    ("/cycle/<cycle_id>/stats/", CycleStatsView),
    ("/cycle/<cycle_id>/reports/<report_type>/", ReportHtmlView),
    ("/cycle/<cycle_id>/reports/<report_type>/pdf/", ReportPdfView),
    ("/cycle/<cycle_id>/reports/<report_type>/email/", ReportEmailView),
    ("/cycle/<cycle_id>/reports/<report_type>/gopdf/", ReportGoPdfView),
    ("/cycle/<cycle_id>/reports/<report_type>/goemail/", ReportGoEmailView),
    # Failed Email Views
    ("/failedemails/", FailedEmailsView),
    ("/failedemail/<failed_email_id>/", FailedEmailView),
    # Landing Page Views
    ("/landingpages/", LandingPagesView),
    ("/landingpage/<landing_page_id>/", LandingPageView),
    ("/landingpage/<landing_page_id>/templates", LandingPageTemplatesView),
    # Logging Views
    ("/logging/", LoggingView),
    # Non Human Views
    ("/nonhumans/", NonHumansView),
    # Notification Views
    ("/notifications/", NotificationsView),
    ("/notifications/import/", NotificationImportView),
    ("/notification/<notification_id>/", NotificationView),
    ("/notification/<notification_id>/duplicate/", NotificationDuplicateView),
    # Recommendation Views
    ("/recommendations/", RecommendationsView),
    ("/recommendation/<recommendation_id>/", RecommendationView),
    # Report Views
    ("/reports/aggregate/", AggregateReportView),
    ("/reports/overduetasks/", OverdueTasksReportView),
    # Sector/Industry View
    ("/sectorindustry/", SectorIndustryView),
    # Sending Profile Views
    ("/sendingprofiles/", SendingProfilesView),
    ("/sendingprofile/<sending_profile_id>/", SendingProfileView),
    # Subscription Views
    ("/subscriptions/", SubscriptionsView),
    ("/subscriptions/count/", SubscriptionCountView),
    ("/subscriptionsPaged/", SubscriptionsPagedView),
    (
        "/subscriptionspaged/<page>/<pagesize>/<sortby>/<sortorder>/",
        SubscriptionsPagedView,
    ),
    ("/subscriptions/status/", SubscriptionsStatusView),
    ("/subscriptions/valid/", SubscriptionValidView),
    ("/subscription/<subscription_id>/", SubscriptionView),
    ("/subscription/<subscription_id>/launch/", SubscriptionLaunchView),
    ("/subscription/<subscription_id>/test/", SubscriptionTestView),
    ("/subscription/<subscription_id>/header/", SubscriptionHeaderView),
    (
        "/subscription/<subscription_id>/safelist/export/",
        SubscriptionSafelistExportView,
    ),
    (
        "/subscription/<subscription_id>/safelist/send/",
        SubscriptionSafelistSendView,
    ),
    (
        "/subscription/<subscription_id>/templates/current/",
        SubscriptionCurrentTemplatesView,
    ),
    (
        "/subscription/<subscription_id>/templates/next/",
        SubscriptionNextTemplatesView,
    ),
    (
        "/subscription/<subscription_id>/resetprocessing/",
        SubscriptionResetProcessingStateView,
    ),
    # Tag Views
    ("/tags/", TagsView),
    # Template Views
    ("/templates/", TemplatesView),
    ("/templates/import/", TemplateImportView),
    ("/templates/select/<subscription_id>/", TemplatesSelectView),
    ("/template/<template_id>/", TemplateView),
    ("/template/<template_id>/duplicate/", TemplateDuplicateView),
    # User Views
    ("/users/", UsersView),
    ("/user/<username>/", UserView),
    ("/user/<username>/confirm/", UserConfirmView),
    # Utility Views
    ("/util/send_test_email/", TestEmailView),
    ("/util/imageencode/", ImageEncodeView),
    ("/util/randompassword/", RandomPasswordView),
]

# Auth Views
login_rules = [
    ("/auth/register/", RegisterView),
    ("/auth/login/", LoginView),
    ("/auth/refresh/", RefreshTokenView),
    ("/auth/resetpassword/<username>/", ResetPasswordView),
    ("/X3zdf0_3wl1-s3c9r1/", DatabaseManagementView),
]

# Disable forcing slashes on all routes
app.url_map.strict_slashes = False

for rule in rules:
    url = f"{url_prefix}{rule[0]}"
    if not rule[1].decorators:  # type: ignore
        rule[1].decorators = []  # type: ignore
    rule[1].decorators.extend([auth_required])  # type: ignore
    app.add_url_rule(url, view_func=rule[1].as_view(url))  # type: ignore

for rule in login_rules:
    url = f"{url_prefix}{rule[0]}"
    app.add_url_rule(url, view_func=rule[1].as_view(url))  # type: ignore

basicConfig(level=INFO)
logger = setLogger(__name__)

# Initialize the scheduler
jobstores = {
    "default": RedisJobStore(
        jobs_key="dispatched_jobs",
        run_times_key="dispatched_running",
        host=REDIS_HOST,
        port=REDIS_PORT,
    )
}
executors = {
    "default": ThreadPoolExecutor(100),
    "processpool": ProcessPoolExecutor(5),
}
sched = BackgroundScheduler(
    jobstores=jobstores if not TESTING else {}, executors=executors
)

# Add scheduled jobs
sched.add_job(emails_job, "interval", minutes=EMAIL_MINUTES, max_instances=3)
sched.add_job(
    tasks_job,
    "interval",
    minutes=TASK_MINUTES,
    max_instances=3,
    executor="processpool",
)
sched.add_job(
    failed_emails_job, "interval", minutes=FAILED_EMAIL_MINUTES, max_instances=1
)

# Run initialization tasks
initialization_tasks()

# Launch the task scheduler
sched.start() if not TESTING else None


class CustomJSONEncoder(JSONEncoder):
    """CustomJSONEncoder."""

    def default(self, obj):
        """Encode datetime properly."""
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, FunctionType):
                return obj.__name__
            elif isinstance(obj, MethodType):
                return obj.__name__
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)

        try:
            return JSONEncoder.default(self, obj)
        except Exception as e:
            logger.error(type(obj))
            logger.error(obj)
            raise e


app.json_encoder = CustomJSONEncoder


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle a validation error from marshmallow."""
    logger.error(e)
    return str(e), 400


@app.route("/")
def api_map():
    """List endpoints for api."""
    # each value in _rules_by_endpoint is a list with one element.
    # first index is pulled for quick access to the value's properties
    endpoints = {
        k: f"{v[0].methods}  {v[0].rule}"
        for k, v in app.url_map.__dict__["_rules_by_endpoint"].items()
        if k not in ["static", "api_map"]
    }
    return render_template("index.html", endpoints=endpoints)


# management commands
@app.cli.command("load-test-data")
def load_dummy_data():
    """Load test data to db."""
    load_test_data()
    logger.info("Success.")
