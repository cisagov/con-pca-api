"""Domain manager."""
# Standard Python Libraries
from datetime import date

# Third-Party Libraries
from flask import Flask, render_template
from flask.json import JSONEncoder
from flask_cors import CORS
from utils.decorators.auth import auth_required

# cisagov Libraries
from api.config import logger
from api.views.auth_views import LoginView, RefreshTokenView, RegisterView
from api.views.user_views import UserConfirmView, UsersView, UserView

app = Flask(__name__, template_folder="templates")
app.url_map.strict_slashes = False
CORS(app)

# register apps
url_prefix = "/api"

rules = [
    ("/users/", UsersView),
    ("/user/<username>/", UserView),
    ("/user/<username>/confirm/", UserConfirmView),
]

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


class CustomJSONEncoder(JSONEncoder):
    """CustomJSONEncoder."""

    def default(self, obj):
        """Encode datetime properly."""
        try:
            if isinstance(obj, date):
                return obj.isoformat()
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


if __name__ == "__main__":
    app.run()
