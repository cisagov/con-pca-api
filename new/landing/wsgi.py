"""Wsgi."""
# Third-Party Libraries
from landing.config import LANDING_HOST, LANDING_PORT
from landing.main import app

if __name__ == "__main__":
    app.run(host=LANDING_HOST, port=LANDING_PORT)
