"""Landing app config."""
# Standard Python Libraries
import os

# https://bandit.readthedocs.io/en/latest/plugins/b104_hardcoded_bind_all_interfaces.html
LANDING_HOST = os.environ.get("LANDING_HOST", "0.0.0.0")  # nosec
LANDING_PORT = os.environ.get("LANDING_PORT", 8000)
