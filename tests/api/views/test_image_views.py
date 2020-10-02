import pytest
from unittest import mock
from faker import Faker
from django.core.files.uploadedfile import InMemoryUploadedFile
from mimetypes import guess_type

fake = Faker()


@pytest.mark.django_db
def test_image_view_post(client):
    with mock.patch(
        "api.utils.aws_utils.S3.upload_fileobj_image"
    ) as mock_upload, mock.patch("boto3.client"):
        uuid = fake.uuid4()
        mock_upload.return_value = uuid, "testbucket", "testurl"

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
        assert mock_upload.called
