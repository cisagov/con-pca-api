"""Failed Email views."""
# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView

# cisagov Libraries
from api.manager import FailedEmailManager
from utils.logging import setLogger

logger = setLogger(__name__)

failed_email_manager = FailedEmailManager()


class FailedEmailView(MethodView):
    """FailedEmailView."""

    def get(self):
        """Get."""
        return jsonify(failed_email_manager.all())
