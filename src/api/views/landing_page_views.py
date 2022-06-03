"""Landing page views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import LandingPageManager, TemplateManager

landing_page_manager = LandingPageManager()
template_manager = TemplateManager()


class LandingPagesView(MethodView):
    """LandingPagesView."""

    def get(self):
        """Get."""
        parameters = landing_page_manager.get_query(request.args)
        pages = landing_page_manager.all(params=parameters)

        for page in pages:
            if page["is_default_template"]:
                default_name = f"(System Default) {page['name']}"
                page["name"] = default_name
                break

        return jsonify(pages)

    def post(self):
        """Post."""
        data = request.json
        landing_page = landing_page_manager.save(data)
        if data["is_default_template"]:
            landing_page_manager.clear_and_set_default(landing_page["_id"])
        return jsonify(landing_page)


class LandingPageView(MethodView):
    """LandingPageView."""

    def get(self, landing_page_id):
        """Get."""
        return jsonify(landing_page_manager.get(document_id=landing_page_id))

    def put(self, landing_page_id):
        """Put."""
        landing_page = landing_page_manager.get(document_id=landing_page_id)
        landing_page.update(request.json)

        if landing_page["is_default_template"]:
            landing_page_manager.clear_and_set_default(landing_page_id)

        landing_page_manager.update(document_id=landing_page_id, data=landing_page)
        return jsonify({"success": True})

    def delete(self, landing_page_id):
        """Delete."""
        landing_page = landing_page_manager.get(document_id=landing_page_id)
        if landing_page.get("is_default_template"):
            return jsonify({"Cannot delete default template."}), 400

        templates = template_manager.all(
            params={"landing_page_id": landing_page_id},
            fields=["template_id", "name"],
        )
        if templates:
            return (
                jsonify(
                    {
                        "error": "A template currently utilizes this landing page.",
                        "templates": templates,
                    }
                ),
                400,
            )
        landing_page_manager.delete(document_id=landing_page_id)
        return jsonify({"success": True})
