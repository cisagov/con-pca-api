"""Domain manager."""
# Third-Party Libraries
from flask import jsonify

# cisagov Libraries
from landing.app import app
from landing.views import ClickView, OpenView
from utils.logging import setLogger

logger = setLogger(__name__)


@app.route("/")
def api_map():
    """List endpoints for api."""
    logger.info("Landing page is running.")
    return jsonify("Con-PCA landing page is running.")


rules = [
    ("/c/<tracking_id>/", ClickView),
    ("/o/<tracking_id>/", OpenView),
]

for rule in rules:
    app.add_url_rule(rule[0], view_func=rule[1].as_view(rule[0]))  # type: ignore
