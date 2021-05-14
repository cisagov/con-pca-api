"""Tests for api.utils.template.selector functions."""
# cisagov Libraries
from api.utils.template import selector


def test_group_template():
    """Test group_template function."""
    result = selector.group_template({"deception_score": 1})
    assert result == "low"
    result = selector.group_template({"deception_score": 4})
    assert result == "moderate"
    result = selector.group_template({"deception_score": 6})
    assert result == "high"


def test_select_templates():
    """Test select_templates function."""
    templates = []
    # Append low templates
    for i in range(0, 3):
        templates.append({"deception_score": 1, "template_uuid": f"low_{i}"})
    # Append moderate templates
    for i in range(0, 7):
        templates.append({"deception_score": 4, "template_uuid": f"moderate_{i}"})
    # Append high templates
    for i in range(0, 20):
        templates.append({"deception_score": 7, "template_uuid": f"high_{i}"})

    result = selector.select_templates(templates)
    assert len(result["low"]) == 3
    assert len(result["moderate"]) == 5
    assert len(result["high"]) == 5
