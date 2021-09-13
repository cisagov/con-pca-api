"""Flask app."""
# Third-Party Libraries
from flask import Flask
from flask_cors import CORS

# cisagov Libraries
from api.initialize import initialize_templates


class CustomApp(Flask):
    """CustomApp."""

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        """Run."""
        with self.app_context():
            initialize_templates()
        super(CustomApp, self).run(
            host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options
        )


app = CustomApp(__name__, template_folder="templates")
app.url_map.strict_slashes = False
CORS(app)
