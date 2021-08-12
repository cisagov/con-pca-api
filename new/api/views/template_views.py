"""Template Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView
from utils.templates import select_templates

# cisagov Libraries
from api.manager import TemplateManager

template_manager = TemplateManager()


class TemplatesView(MethodView):
    """TemplatesView."""

    def get(self):
        """Get."""
        # Allow querying a list of templates
        parameters = template_manager.get_query(request.args)
        templates = request.args.get("templates")
        if templates:
            parameters["template_uuid"] = {"$in": templates.split(",")}
        print(parameters)
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
        template = template_manager.get(uuid=template_uuid)
        template.update(data)

        # TODO: Validate Template
        return jsonify(template_manager.update(uuid=template_uuid, data=template))

    def delete(self, template_uuid):
        """Delete."""
        template = template_manager.get(uuid=template_uuid)

        if not template.get("retired"):
            return jsonify({"error": "You must retire the template first."}), 400

        # TODO: Check if used in any campaigns

        # TODO: Check if subscription has template in list of templates

        return jsonify(template_manager.delete(uuid=template_uuid))


# TODO: TemplateStopView
# TODO: Send Test Email View
# TODO: Import Email View
class TemplatesSelectView(MethodView):
    """TemplateSelectView."""

    def get(self):
        """Get."""
        templates = template_manager.all({"retired": False})
        return jsonify(select_templates(templates))
