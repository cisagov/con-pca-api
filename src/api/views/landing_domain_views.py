"""Landing domain views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import LandingDomainManager, SubscriptionManager

landing_domain_manager = LandingDomainManager()
subscription_manager = SubscriptionManager()


class LandingDomainsView(MethodView):
    """LandingDomainsView."""

    def get(self):
        """Get."""
        return jsonify(landing_domain_manager.all())

    def post(self):
        """Post."""
        return jsonify(landing_domain_manager.save(request.json))


class LandingDomainView(MethodView):
    """LandingDomainView."""

    def get(self, landing_domain_id):
        """Get."""
        return jsonify(landing_domain_manager.get(document_id=landing_domain_id))

    def put(self, landing_domain_id):
        """Put."""
        return jsonify(
            landing_domain_manager.update(
                document_id=landing_domain_id, data=request.json
            )
        )

    def delete(self, landing_domain_id):
        """Delete."""
        subscriptions = subscription_manager.all(
            params={"landing_domain_id": landing_domain_id},
            fields=["_id", "name"],
        )
        if subscriptions:
            return jsonify(
                {
                    "error": "Subscriptions utilizing landing domain.",
                    "subscriptions": subscriptions,
                }
            )
        return jsonify(landing_domain_manager.delete(document_id=landing_domain_id))
