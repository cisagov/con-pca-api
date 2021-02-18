"""Export Lambda Function."""
# Standard Python Libraries
import json
import os

# Third-Party Libraries
import boto3

# cisagov Libraries
from api import services
from api.utils.generic import format_json

s3 = boto3.client("s3")
EXPORT_BUCKET = os.environ["AWS_S3_EXPORT_BUCKET"]


def lambda_handler(event, context):
    """Export all collections to S3."""
    collections = list(filter(lambda x: x.endswith("Service"), dir(services)))
    for collection in collections:
        if collection != "DBService":
            service = getattr(services, collection)()
            data = service.get_list()
            s3.put_object(
                Body=json.dumps(data, default=format_json),
                Bucket=EXPORT_BUCKET,
                Key=f"{collection}.json",
            )


if __name__ == "__main__":
    lambda_handler(None, None)
