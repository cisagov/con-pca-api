# Standard Python Libraries
import logging
import os
import uuid
from config import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from django.contrib.staticfiles.storage import staticfiles_storage

# Third-Party Libraries
import boto3

logger = logging.getLogger()


class AWS:
    def get_client(self, service):
        return boto3.client(service_name=service)


class S3(AWS):
    def __init__(self):
        self.client = self.get_client("s3")
        self.image_bucket = os.environ.get("AWS_S3_IMAGE_BUCKET")

    def upload_fileobj_image(self, data):
        key = f"{uuid.uuid4().hex}.png"
        logger.info(f"data={data} bucket={self.image_bucket} key={key}")
        self.client.upload_fileobj(data, self.image_bucket, key)
        host = "https://s3.amazonaws.com"
        url = f"{host}/{self.image_bucket}/{key}"

        return key, self.image_bucket, url


class SES(AWS):
    def __init__(self):
        if settings.SES_ASSUME_ROLE_ARN:
            sts = STS()
            self.client = sts.assume_role_client("ses", settings.SES_ASSUME_ROLE_ARN)
        else:
            self.client = self.get_client("ses")

    def send_message(
        self,
        sender: str,
        to: list,
        subject: str,
        bcc: list = None,
        text: str = None,
        html: str = None,
        attachments: list = None,
        binary_attachments: list = None,
    ):
        msg = self._create_multipart_message(
            sender=sender,
            to=to,
            subject=subject,
            bcc=bcc,
            text=text,
            html=html,
            attachments=attachments,
            binary_attachments=binary_attachments,
        )
        return self.client.send_raw_email(RawMessage={"Data": msg.as_string()})

    def _create_multipart_message(
        self,
        sender: str,
        to: list,
        subject: str,
        bcc: list = None,
        text: str = None,
        html: str = None,
        attachments: list = None,
        binary_attachments: list = None,
    ) -> MIMEMultipart:
        multipart_content_subtype = "alternative" if text and html else "mixed"
        msg = MIMEMultipart(multipart_content_subtype)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(to)
        msg["Bcc"] = ", ".join(bcc)

        # Record the MIME types of both parts - text/plain and text/html.
        # According to RFC 2046, the last part of a multipart message, in this case the HTML message, is best and preferred.
        if text:
            part = MIMEText(text, "plain")
            msg.attach(part)
        if html:
            part = MIMEText(html, "html")
            msg.attach(part)

        # Add attachments
        for attachment in attachments or []:
            with staticfiles_storage.open(attachment) as f:
                part = MIMEApplication(f.read())
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(attachment),
                )
                msg.attach(part)

        for ba in binary_attachments or []:
            logging.info("Adding binary attachment")
            part = MIMEApplication(ba["data"], _subtype="pdf")
            part.add_header(
                "Content-Disposition", "attachment", filename=ba["filename"]
            )
            msg.attach(part)

        return msg


class STS(AWS):
    def __init__(self):
        self.client = self.get_client("sts")

    def assume_role_client(self, service, role_arn):
        resp = self.client.assume_role(
            RoleArn=role_arn, RoleSessionName=f"{service}_session"
        )

        return boto3.client(
            service,
            aws_access_key_id=resp["Credentials"]["AccessKeyId"],
            aws_secret_access_key=resp["Credentials"]["SecretAccessKey"],
            aws_session_token=resp["Credentials"]["SessionToken"],
        )
