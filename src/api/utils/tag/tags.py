from api.utils import db_utils as db
from api.models.template_models import TagModel, validate_tag
from faker import Faker

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


def get_faker_tags(with_values: bool = False):
    fake = Faker()
    tags = []
    for func in dir(fake):
        try:
            if (
                callable(getattr(fake, func))
                and not func.startswith("_")
                and not func.startswith("add_")
                and not func.startswith("get_")
                and not func.startswith("seed_")
                and not func.startswith("set_")
                and func not in ["format", "parse", "provider", "binary", "tar", "zip"]
            ):
                tag = {
                    "data_source": f"faker_{func}".lower(),
                    "description": f"Faker generated {func}",
                    "tag": f"<%FAKER_{func.upper()}%>",
                    "tag_type": "con-pca-eval",
                }
                if with_values:
                    tag["value"] = str(getattr(fake, func)())

                tags.append(tag)
        except Exception:
            pass
    return tags
