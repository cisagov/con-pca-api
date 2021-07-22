"""Image View Tests."""
# Standard Python Libraries
from mimetypes import guess_type

# Third-Party Libraries
from django.core.files.uploadedfile import InMemoryUploadedFile
import pytest


@pytest.mark.django_db
def test_image_view_post(client):
    """Test Image View Post."""
    name = "src/static/img/cisa_logo.png"
    with open(name, "rb") as f:
        f.seek(0)
        f.read()
        size = f.tell()
        f.seek(0)
        content_type, charset = guess_type(name)
        uf = InMemoryUploadedFile(
            file=f,
            name=name,
            field_name=None,
            content_type=content_type,
            size=size,
            charset=charset,
        )
        resp = client.post("/api/v1/imageupload/", data={"file": uf})
    assert resp.status_code == 201
    assert resp.json()["imageUrl"].startswith("data:image/jpeg;base64")
