# Standard Python Libraries
import logging
import os
from urllib.parse import urlparse
import uuid

# Third-Party Libraries
import boto3

logger = logging.getLogger()


class AWS:
    def __init__(self):
        if os.environ.get("AWS_ENDPOINT_URL"):
            self.endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
            self.use_ssl = False
        else:
            self.endpoint_url = None
            self.use_ssl = True

    def get_client(self, service):
        return boto3.client(
            service_name=service, endpoint_url=self.endpoint_url, use_ssl=self.use_ssl,
        )


class S3(AWS):
    def __init__(self):
        super().__init__()
        self.client = self.get_client("s3")
        self.image_bucket = os.environ.get("AWS_S3_IMAGE_BUCKET")

    def upload_fileobj_image(self, data):
        key = f"{uuid.uuid4().hex}.png"
        logger.info(f"data={data} bucket={self.image_bucket} key={key}")
        self.client.upload_fileobj(data, self.image_bucket, key)

        # Replace the url for local stack container location with local host
        # Required so that docker containers can communincate with one another but still allow
        # the tester to retreive the image on there local machine
        if self.endpoint_url:
            parsed_url = urlparse(self.endpoint_url)
            external_host = os.environ.get("AWS_S3_EXTERNAL_HOST", "localhost")
            host = f"{parsed_url.scheme}://{external_host}:{parsed_url.port}"
        else:
            host = "https://s3.amazonaws.com"

        url = f"{host}/{self.image_bucket}/{key}"

        return key, self.image_bucket, url
