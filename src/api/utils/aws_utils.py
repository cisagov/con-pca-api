"""AWS Utils."""
# Standard Python Libraries
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Third-Party Libraries
import boto3

# cisagov Libraries
from config import settings
from config.settings import COGNITO_CLIENT_ID, COGNITO_USER_POOL_ID


class AWS:
    """Base AWS Class."""

    def get_client(self, service):
        """Get Client."""
        return boto3.client(service_name=service)


class SES(AWS):
    """SES."""

    def __init__(self):
        """Create SES Client."""
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
        bcc: list = [],
        text: str = None,
        html: str = None,
        attachments: list = None,
        binary_attachments: list = None,
    ):
        """Send message via SES."""
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
        bcc: list = [],
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
            msg.attach(MIMEText(text, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        # Add attachments
        for attachment in attachments or []:
            with open(attachment, "rb") as f:
                file_part = MIMEApplication(f.read())
                file_part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(attachment),
                )
                msg.attach(file_part)

        for ba in binary_attachments or []:
            bin_part = MIMEApplication(ba["data"], _subtype="pdf")
            bin_part.add_header(
                "Content-Disposition", "attachment", filename=ba["filename"]
            )
            msg.attach(bin_part)

        return msg


class STS(AWS):
    """STS."""

    def __init__(self):
        """Create STS Client."""
        self.client = self.get_client("sts")

    def assume_role_client(self, service, role_arn):
        """Assume Role via STS."""
        resp = self.client.assume_role(
            RoleArn=role_arn, RoleSessionName=f"{service}_session"
        )

        return boto3.client(
            service,
            aws_access_key_id=resp["Credentials"]["AccessKeyId"],
            aws_secret_access_key=resp["Credentials"]["SecretAccessKey"],
            aws_session_token=resp["Credentials"]["SessionToken"],
        )


class Cognito(AWS):
    """Cognito."""

    def __init__(self):
        """Create cognito client."""
        self.client = self.get_client("cognito-idp")

    def list_users(self):
        """List users."""
        return self.client.list_users(UserPoolId=COGNITO_USER_POOL_ID)["Users"]

    def delete_user(self, username):
        """Delete user."""
        return self.client.admin_delete_user(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )

    def confirm_user(self, username):
        """Confirm user."""
        return self.client.admin_confirm_sign_up(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )

    def sign_up(self, username, password, email):
        """Sign up user."""
        return self.client.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}],
        )

    def authenticate(self, username, password):
        """Authenticate user."""
        return self.client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
            ClientMetadata={
                "username": username,
                "password": password,
            },
        )

    def refresh(self, token):
        """Refresh auth token."""
        return self.client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": token},
        )
