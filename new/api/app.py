"""Flask app."""
# Third-Party Libraries
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")
app.url_map.strict_slashes = False
CORS(app)
Bootstrap(app)


print("test")
