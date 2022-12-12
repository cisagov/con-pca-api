"""Cycle view."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CycleManager
from utils.mongo_stats import mongo_get_cycle_stats
from utils.stats import get_cycle_stats

cycle_manager = CycleManager()


class CyclesView(MethodView):
    """CyclesView."""

    def get(self):
        """Get."""
        parameters = cycle_manager.get_query(request.args)
        return jsonify(
            cycle_manager.all(
                params=parameters,
                fields=[
                    "_id",
                    "subscription_id",
                    "template_ids",
                    "start_date",
                    "end_date",
                    "send_by_date",
                    "active",
                    "target_count",
                    "phish_header",
                    "manual_reports",
                ],
            )
        )


class CycleView(MethodView):
    """CycleView."""

    def get(self, cycle_id):
        """Get a cycle."""
        return cycle_manager.get(document_id=cycle_id)

    def delete(self, cycle_id):
        """Delete a cycle."""
        cycle_manager.delete(document_id=cycle_id)
        return jsonify({"success": True})


class CycleStatsView(MethodView):
    """CycleStatsView."""

    def get(self, cycle_id):
        """Get."""
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True
        recalculate = False
        if request.args.get("recalculate", "") == "true":
            recalculate = True
        cycle = cycle_manager.get(document_id=cycle_id)
        get_cycle_stats(cycle, recalculate)
        return jsonify(cycle["nonhuman_stats"] if nonhuman else cycle["stats"])


class MongoCycleStatsView(MethodView):
    """MongoCycleStatsView."""

    def get(self, cycle_id):
        """Get."""
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True
        recalculate = False
        if request.args.get("recalculate", "") == "true":
            recalculate = True
        cycle = cycle_manager.get(document_id=cycle_id)
        mongo_get_cycle_stats(cycle, recalculate)
        return jsonify(cycle["nonhuman_stats"] if nonhuman else cycle["stats"])


class CycleManualReportsView(MethodView):
    """CycleReportsView."""

    def post(self, cycle_id):
        """Update manual reports."""
        cycle_manager.update(
            document_id=cycle_id,
            data={
                "manual_reports": request.json["manual_reports"],
                "dirty_stats": True,
            },
        )
        return jsonify({"success": True})
