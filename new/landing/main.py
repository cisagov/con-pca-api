"""Domain manager."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from flask.templating import render_template_string
from landing.app import app
from landing.views import ClickView, OpenView


@app.route("/")
def api_map():
    """List endpoints for api."""
    logging.info("Landing page is running.")
    return render_template_string("404 Not Found"), 404


rules = [
    ("/c/<tracking_id>/", ClickView),
    ("/o/<tracking_id>/", OpenView),
]

for rule in rules:
    app.add_url_rule(rule[0], view_func=rule[1].as_view(rule[0]))
