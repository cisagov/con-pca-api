"""Flask app."""
# Third-Party Libraries
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, template_folder="templates")
app.url_map.strict_slashes = False
app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore
CORS(app)
