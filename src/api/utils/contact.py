"""Contact utils."""


def format_contact_name(contact):
    """Format a contact first and last name."""
    return f"{contact.get('first_name')} {contact.get('last_name')}"
