import pytest
from unittest import mock
from faker import Faker


fake = Faker()


def template():
    return {
        "appearance": {"grammar": 0, "link_domain": 1, "logo_graphics": 0},
        "behavior": {"curiosity": 1, "duty_obligation": 0, "fear": 0, "greed": 0},
        "deception_score": 1,
        "description": "Intern Resume",
        "descriptive_words": "student resumes internship intern",
        "from_address": "<%FAKER_FIRST_NAME%> <%FAKER_LAST_NAME%> <<%FAKER_FIRST_NAME%>.<%FAKER_LAST_NAME%>@domain.com>",
        "html": "<br>Hi, sorry, I don't know exactly who this would go to. I read on the site<br>that your accepting student resumes for a summe rinternship. I'ev loaded<br>mine to our school's website. Please review and let me know if we're good to<br>go.<br><a href=\"<%URL%>\">https://endermannpoly.edu/studentresources/resumes/mquesenberry3.pdf</a><br><br><br>thx, <%FAKER_FIRST_NAME%>&nbsp;<br>",
        "name": "Intern Resume",
        "relevancy": {"organization": 0, "public_news": 0},
        "retired": False,
        "retired_description": "",
        "sender": {"authoritative": 0, "external": 0, "internal": 0},
        "subject": "Intern Resume",
        "text": "Hi, sorry, I don't know exactly who this would go to. I read on the sitethat your accepting student resumes for a summe rinternship. I'ev loadedmine to our school's website. Please review and let me know if we're good togo.https://endermannpoly.edu/studentresources/resumes/mquesenberry3.pdfthx, <%FAKER_FIRST_NAME%>\u00a0",
    }


def template_post():
    return {
        "appearance": {"grammar": 0, "link_domain": 1, "logo_graphics": 0},
        "behavior": {"curiosity": 1, "duty_obligation": 0, "fear": 0, "greed": 0},
        "deception_score": 1,
        "description": "Intern Resume",
        "descriptive_words": "student resumes internship intern",
        "from_address": "<%FAKER_FIRST_NAME%> <%FAKER_LAST_NAME%> <<%FAKER_FIRST_NAME%>.<%FAKER_LAST_NAME%>@domain.com>",
        "html": "<br>Hi, sorry, I don't know exactly who this would go to. I read on the site<br>that your accepting student resumes for a summe rinternship. I'ev loaded<br>mine to our school's website. Please review and let me know if we're good to<br>go.<br><a href=\"<%URL%>\">https://endermannpoly.edu/studentresources/resumes/mquesenberry3.pdf</a><br><br><br>thx, <%FAKER_FIRST_NAME%>&nbsp;<br>",
        "name": "Intern Resume",
        "relevancy": {"organization": 0, "public_news": 0},
        "retired": False,
        "retired_description": "",
        "sender": {"authoritative": 0, "external": 0, "internal": 0},
        "subject": "Intern Resume",
        "text": "Hi, sorry, I don't know exactly who this would go to. I read on the sitethat your accepting student resumes for a summe rinternship. I'ev loadedmine to our school's website. Please review and let me know if we're good togo.https://endermannpoly.edu/studentresources/resumes/mquesenberry3.pdfthx, <%FAKER_FIRST_NAME%>\u00a0",
    }


def template_post_response():
    return {"template_uuid": "1234"}


@pytest.mark.django_db
def test_templates_view_list_get(client):
    with mock.patch(
        "api.services.TemplateService.get_list",
        return_value=[template()],
    ) as mock_get_list:
        result = client.get("/api/v1/templates/")
        assert mock_get_list.called
        assert result.status_code == 200

        result = client.get("/api/v1/templates/", {"subject": "foo bar"})
        assert mock_get_list.called
        assert result.status_code == 200


@pytest.mark.django_db
def test_templates_view_list_post(client):
    with mock.patch(
        "api.services.TemplateService.save",
        return_value=template_post_response(),
    ) as mock_post, mock.patch(
        "api.services.TemplateService.exists",
        return_value=False,
    ) as mock_exists:
        result = client.post("/api/v1/templates/", template_post())
        assert mock_post.called
        assert mock_exists.called
        assert result.status_code == 201

    with mock.patch(
        "api.services.TemplateService.save",
        return_value=template_post_response(),
    ) as mock_post, mock.patch(
        "api.services.TemplateService.exists",
        return_value=True,
    ) as mock_exists:
        result = client.post("/api/v1/templates/", template_post())
        assert not mock_post.called
        assert mock_exists.called
        assert result.status_code == 409
