"""Flask request helpers."""
# Third-Party Libraries
from flask import request


def get_request_ip():
    """Get request ip."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"]
    else:
        return request.remote_addr
