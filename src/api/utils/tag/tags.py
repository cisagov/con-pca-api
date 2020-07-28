from api.utils import db_utils as db
from api.models.template_models import TagModel, validate_tag

import re


def get_tags():
    return db.get_list(None, "tag_definition", TagModel, validate_tag)


def check_tag_format(tag):
    """Check_tag_format.

    Checks if the given string is in the format required for a tag.
    Correct: <%TEST_TAG%>
    Args:
        tag (string): Tag string from tag object

    Returns:
        bool: True if in correct format, false otherwise.
    """
    r = re.compile("<%.*%>")
    if r.match(tag) is not None and tag.isupper():
        return True
    return False
