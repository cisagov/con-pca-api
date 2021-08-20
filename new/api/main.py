"""Domain manager."""
# Standard Python Libraries
from datetime import date
from types import FunctionType, MethodType

# Third-Party Libraries
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template
from flask.json import JSONEncoder
from utils.decorators.auth import auth_required

# cisagov Libraries
from api.app import app
from api.config import logger
from api.phish import emails_job
from api.views.auth_views import LoginView, RefreshTokenView, RegisterView
from api.views.customer_views import CustomersView, CustomerView, SectorIndustryView
from api.views.cycle_views import CycleStatsView, CyclesView, CycleView
from api.views.landing_page_views import LandingPagesView, LandingPageView
from api.views.sending_profile_views import SendingProfilesView, SendingProfileView
from api.views.subscription_views import (
    SubscriptionLaunchView,
    SubscriptionsView,
    SubscriptionView,
)
from api.views.tag_views import TagsView
from api.views.template_views import TemplatesSelectView, TemplatesView, TemplateView
from api.views.user_views import UserConfirmView, UsersView, UserView
from api.views.utility_views import TestEmailView

# register apps
url_prefix = "/api"

rules = [
    # Customer Views
    ("/customers/", CustomersView),
    ("/customer/<customer_uuid>/", CustomerView),
    # Cycle Views
    ("/cycles/", CyclesView),
    ("/cycle/<cycle_uuid>/", CycleView),
    ("/cycle/<cycle_uuid>/stats/", CycleStatsView),
    # Landing Page Views
    ("/landingpages/", LandingPagesView),
    ("/landingpage/<landing_page_uuid>/", LandingPageView),
    # Sector/Industry View
    ("/sectorindustry/", SectorIndustryView),
    # Sending Profile Views
    ("/sendingprofiles/", SendingProfilesView),
    ("/sendingprofile/<sending_profile_uuid>/", SendingProfileView),
    # Subscription Views
    ("/subscriptions/", SubscriptionsView),
    ("/subscription/<subscription_uuid>/", SubscriptionView),
    ("/subscription/<subscription_uuid>/launch/", SubscriptionLaunchView),
    # Tag Views
    ("/tags/", TagsView),
    # Template Views
    ("/templates/", TemplatesView),
    ("/templates/select/", TemplatesSelectView),
    ("/template/<template_uuid>/", TemplateView),
    # User Views
    ("/users/", UsersView),
    ("/user/<username>/", UserView),
    ("/user/<username>/confirm/", UserConfirmView),
    # Utility Views
    ("/util/send_test_email/", TestEmailView),
]

# Auth Views
login_rules = [
    ("/auth/register/", RegisterView),
    ("/auth/login/", LoginView),
    ("/auth/refresh/", RefreshTokenView),
]

for rule in rules:
    url = f"{url_prefix}{rule[0]}"
    if not rule[1].decorators:
        rule[1].decorators = []
    rule[1].decorators.extend([auth_required])
    app.add_url_rule(url, view_func=rule[1].as_view(url))

for rule in login_rules:
    url = f"{url_prefix}{rule[0]}"
    app.add_url_rule(url, view_func=rule[1].as_view(url))

sched = BackgroundScheduler()
sched.add_job(emails_job, "interval", minutes=1)
sched.start()


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
        return JSONEncoder.default(self, obj)


app.json_encoder = CustomJSONEncoder


@app.route("/")
def api_map():
    """List endpoints for api."""
    logger.info("API is up and running.")
    endpoints = {
        endpoint.rule: endpoint.methods
        for endpoint in app.url_map.__dict__["_rules"]
        if endpoint.rule not in ["/static/<path:filename>", "/"]
    }
    return render_template("index.html", endpoints=endpoints)
