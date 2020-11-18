"""AWS Util Tests."""
# Standard Python Libraries
from io import BytesIO
import os
from unittest import mock

# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from src.api.utils import aws_utils

fake = Faker()


@mock.patch("boto3.client")
def test_get_client(mock_client):
    """Test Client."""
    aws = aws_utils.AWS()
    aws.get_client("s3")
    assert mock_client.called


@mock.patch("boto3.client")
def test_s3(mock_client):
    """Test S3."""
    os.environ["AWS_S3_IMAGE_BUCKET"] = "test_bucket"
    s3 = aws_utils.S3()
    mock_client.assert_called_with(service_name="s3")
    assert s3.image_bucket == "test_bucket"

    buffer = BytesIO(fake.binary())
    key, bucket, url = s3.upload_fileobj_image(buffer)
    assert type(key) is str
    assert bucket == "test_bucket"
    assert url == f"https://s3.amazonaws.com/test_bucket/{key}"


@mock.patch("boto3.client")
def test_ses(mock_client):
    """Test SES."""
    ses = aws_utils.SES()
    ses.send_message(
        sender=fake.email(),
        to=[fake.email()],
        subject=fake.word(),
        bcc=[fake.email()],
        text=fake.paragraph(),
        html=fake.paragraph(),
        attachments=["src/static/img/cisa_logo.png"],
        binary_attachments=[{"filename": "test", "data": fake.binary()}],
    )

    assert mock_client.call_count > 0


@mock.patch("boto3.client")
def test_sts(mock_client):
    """Test STS."""
    sts = aws_utils.STS()
    mock_client.assert_called_with(service_name="sts")
    sts.assume_role_client("s3", "testarn")
    assert mock_client.mock_calls[1].kwargs == {
        "RoleArn": "testarn",
        "RoleSessionName": "s3_session",
    }
