"""Non human views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CycleManager, NonHumanManager
from utils.stats import get_nonhuman_orgs

nonhuman_manager = NonHumanManager()
cycle_manager = CycleManager()


class NonHumansView(MethodView):
    """NonHumansView."""

    def get(self):
        """Get."""
        nonhumans = get_nonhuman_orgs()
        return jsonify(nonhumans)

    def post(self):
        """Post."""
        data = request.data.decode("utf-8")
        nonhumans = get_nonhuman_orgs()
        if data in nonhumans:
            return jsonify("Nonhuman org already exists."), 400
        nonhuman_manager.save({"asn_org": data})
        cycle_manager.update_many({}, {"dirty_stats": True})
        return jsonify({"success": True})

    def delete(self):
        """Delete."""
        data = request.data.decode("utf-8")
        nonhuman_manager.delete(params={"asn_org": data})
        cycle_manager.update_many({}, {"dirty_stats": True})
        return jsonify({"success": True})
