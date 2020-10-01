from src.api.utils import aws_utils
import os
from unittest import mock
from io import BytesIO
from faker import Faker

fake = Faker()


@mock.patch("boto3.client")
def test_get_client(mock_client):
    aws = aws_utils.AWS()
    aws.get_client("s3")
    assert mock_client.called


@mock.patch("boto3.client")
def test_s3(mock_client):
    os.environ["AWS_S3_IMAGE_BUCKET"] = "test_bucket"
    s3 = aws_utils.S3()
    print(mock_client.call_args)
    mock_client.assert_called_with(service_name="s3")
    assert s3.image_bucket == "test_bucket"

    buffer = BytesIO(fake.binary())
    key, bucket, url = s3.upload_fileobj_image(buffer)
    assert type(key) is str
    assert bucket == "test_bucket"
    assert url == f"https://s3.amazonaws.com/test_bucket/{key}"
