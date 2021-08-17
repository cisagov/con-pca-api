"""Landing page views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import LandingPageManager

landing_page_manager = LandingPageManager()


class LandingPagesView(MethodView):
    """LandingPagesView."""

    def get(self):
        """Get."""
        parameters = landing_page_manager.get_query(request.args)
        with_default = bool(request.args.get("with_default"))
        pages = landing_page_manager.all(params=parameters)

        for page in pages:
            if page["is_default_template"]:
                default_landing_page = page.copy()
                default_landing_page["name"] = (
                    "(System Default)" + default_landing_page["name"]
                )
                default_landing_page["landing_page_uuid"] = 0
                if with_default:
                    pages.append(default_landing_page)
                break

        return jsonify(pages)

    def post(self):
        """Post."""
        data = request.json
        if landing_page_manager.exists({"name": data["name"]}):
            return jsonify({"error": "Landing page exists with that name."}), 400
        landing_page = landing_page_manager.save(data)
        if data["is_default_template"]:
            landing_page_manager.clear_and_set_default(
                landing_page["landing_page_uuid"]
            )
        return jsonify(landing_page)


class LandingPageView(MethodView):
    """LandingPageView."""

    def get(self, landing_page_uuid):
        """Get."""
        return jsonify(landing_page_manager.get(uuid=landing_page_uuid))

    def put(self, landing_page_uuid):
        """Put."""
        landing_page = landing_page_manager.get(uuid=landing_page_uuid)
        landing_page.update(request.json)

        if landing_page["is_default_template"]:
            landing_page_manager.clear_and_set_default(landing_page_uuid)

        landing_page_manager.update(uuid=landing_page_uuid, data=landing_page)
        return jsonify({"success": True})

    def delete(self, landing_page_uuid):
        """Delete."""
        # TODO check if templates are using landing page
        return jsonify(landing_page_manager.delete(uuid=landing_page_uuid))
