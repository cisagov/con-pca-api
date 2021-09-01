"""Cycle view."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView
from utils.stats import get_cycle_stats

# cisagov Libraries
from api.manager import CycleManager

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
                    "cycle_uuid",
                    "subscription_uuid",
                    "template_uuids",
                    "start_date",
                    "end_date",
                    "send_by_date",
                    "active",
                    "target_count",
                ],
            )
        )


class CycleView(MethodView):
    """CycleView."""

    def get(self, cycle_uuid):
        """Get."""
        return cycle_manager.get(uuid=cycle_uuid)


class CycleStatsView(MethodView):
    """CycleStatsView."""

    def get(self, cycle_uuid):
        """Get."""
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True
        cycle = cycle_manager.get(uuid=cycle_uuid)
        stats = get_cycle_stats(cycle, nonhuman)
        return jsonify(stats)
