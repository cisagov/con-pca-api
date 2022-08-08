"""Template Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import (
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
    TemplateManager,
)
from utils.emails import parse_email
from utils.templates import select_templates

template_manager = TemplateManager()
sp_manager = SendingProfileManager()
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
            parameters["_id"] = {"$in": templates.split(",")}

        parameters["retired"] = {"$in": [False, None]}
        if request.args.get("retired", "").lower() == "true":
            parameters["retired"] = True

        templates = []
        for template in template_manager.all(params=parameters):
            sending_profile_id = template.get("sending_profile_id")
            template["sending_profile_domain"] = ""
            if sending_profile_id:
                sending_profile = sp_manager.get(document_id=sending_profile_id)
                template["sending_profile_domain"] = sending_profile[
                    "from_address"
                ].split("@")[1]
            templates.append(template)
        return jsonify(templates)

    def post(self):
        """Post."""
        return jsonify(template_manager.save(request.json))


class TemplateView(MethodView):
    """TemplateView."""

    def get(self, template_id):
        """Get."""
        return jsonify(template_manager.get(document_id=template_id))

    def put(self, template_id):
        """Put."""
        data = request.json
        if data.get("landing_page_id") in ["0", None]:
            data["landing_page_id"] = None

        template = template_manager.get(document_id=template_id)
        template.update(data)
        template_manager.update(document_id=template_id, data=template)
        cycle_manager.update_many(
            params={"template_ids": template_id}, data={"dirty_stats": True}
        )
        return jsonify({"success": True})

    def delete(self, template_id):
        """Delete."""
        template = template_manager.get(document_id=template_id)

        if not template.get("retired"):
            return jsonify({"error": "You must retire the template first."}), 400

        cycles = cycle_manager.all(
            params={"template_ids": template_id}, fields=["subscription_id"]
        )
        if cycles:
            cycle_subs = subscription_manager.all(
                params={"_id": {"$in": {c["subscription_id"] for c in cycles}}},
                fields=["_id", "name"],
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
            params={"templates_selected": template_id},
            fields=["_id", "name"],
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

        template_manager.delete(document_id=template_id)
        return jsonify({"success": True})


class TemplateImportView(MethodView):
    """TemplateImportView."""

    def post(self):
        """Post."""
        # TODO: Support email files
        payload = request.json["content"]
        convert_links = request.json["convert_link"]
        subject, html, text = parse_email(payload, convert_links)
        return jsonify({"subject": subject, "html": html, "text": text})


class TemplatesSelectView(MethodView):
    """TemplateSelectView."""

    def get(self, subscription_id):
        """Get."""
        cycles = cycle_manager.all(
            params={
                "subscription_id": subscription_id,
            },
            fields=["template_ids"],
        )
        previous_template_ids = {
            template_id
            for list in [cycle["template_ids"] for cycle in cycles]
            for template_id in list
        }
        templates = [
            t
            for t in template_manager.all({"retired": False})
            if t["_id"] not in previous_template_ids
        ]
        return jsonify(select_templates(templates))


class TemplateDuplicateView(MethodView):
    """Duplicate an existing Template."""

    def get(self, template_id):
        """Get."""
        template = template_manager.get(document_id=template_id)
        template["name"] = f"{template['name']} COPY"

        return jsonify(template_manager.save(template))
