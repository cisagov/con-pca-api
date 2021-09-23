"""Template Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CycleManager, SubscriptionManager, TemplateManager
from utils.emails import convert_html_links, get_text_from_html
from utils.templates import select_templates

template_manager = TemplateManager()
subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()


class TemplatesView(MethodView):
    """TemplatesView."""

    def get(self):
        """Get."""
        # Allow querying a list of templates
        parameters = template_manager.get_query(request.args)
        templates = request.args.get("templates")
        if templates:
            parameters["template_uuid"] = {"$in": templates.split(",")}

        parameters["retired"] = {"$in": [False, None]}
        if request.args.get("retired", "").lower() == "true":
            parameters["retired"] = True
        return jsonify(template_manager.all(params=parameters))

    def post(self):
        """Post."""
        data = request.json
        if template_manager.exists({"name": data["name"]}):
            return jsonify({"error": "Template with that name already exists."}), 400

        # TODO: Validate Template
        return jsonify(template_manager.save(data))


class TemplateView(MethodView):
    """TemplateView."""

    def get(self, template_uuid):
        """Get."""
        return template_manager.get(uuid=template_uuid)

    def put(self, template_uuid):
        """Put."""
        data = request.json
        if data.get("landing_page_uuid") in ["0", None]:
            data["landing_page_uuid"] = None

        if data.get("retired"):
            subscriptions = subscription_manager.all(
                params={"templates_selected": template_uuid},
                fields=["subscription_uuid", "name"],
            )
            if subscriptions:
                return (
                    jsonify(
                        {
                            "error": "Subscriptions are currently utilizing this template.",
                            "subscriptions": subscriptions,
                        }
                    ),
                    400,
                )

        template = template_manager.get(uuid=template_uuid)
        template.update(data)

        # TODO: Validate Template
        template_manager.update(uuid=template_uuid, data=template)
        return jsonify({"success": True})

    def delete(self, template_uuid):
        """Delete."""
        template = template_manager.get(uuid=template_uuid)

        if not template.get("retired"):
            return jsonify({"error": "You must retire the template first."}), 400

        cycles = cycle_manager.all(
            params={"template_uuids": template_uuid}, fields=["subscription_uuid"]
        )
        if cycles:
            cycle_subs = subscription_manager.all(
                params={
                    "subscription_uuid": {
                        "$in": {c["subscription_uuid"] for c in cycles}
                    }
                },
                fields=["subscription_uuid", "name"],
            )
            return (
                jsonify(
                    {
                        "error": "Subscriptions are currently utilizing this template.",
                        "subscriptions": cycle_subs,
                    }
                ),
                400,
            )

        subscriptions = subscription_manager.all(
            params={"templates_selected": template_uuid},
            fields=["subscription_uuid", "name"],
        )
        if subscriptions:
            return (
                jsonify(
                    {
                        "error": "Subscriptions are currently utilizing this template.",
                        "subscriptions": subscriptions,
                    }
                ),
                400,
            )

        return jsonify(template_manager.delete(uuid=template_uuid))


# TODO: TemplateStopView
class TemplateImportView(MethodView):
    """TemplateImportView."""

    def post(self):
        """Post."""
        # TODO: Support email files
        #   Return subject of email
        html = request.json["content"]
        # TODO: Convert html links only if specified.
        html = convert_html_links(html)
        text = get_text_from_html(html)
        return jsonify({"text": text, "html": html})


class TemplatesSelectView(MethodView):
    """TemplateSelectView."""

    def get(self):
        """Get."""
        templates = template_manager.all({"retired": False})
        return jsonify(select_templates(templates))
