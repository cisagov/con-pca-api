"""Validate formatting utils."""
# Standard Python Libraries
import re


def is_valid_domain(domain: str):
    """Validate domain format."""
    return re.fullmatch(r"\b[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", domain)


def is_validate_email(email: str):
    """Validate domain format."""
    return re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email)
