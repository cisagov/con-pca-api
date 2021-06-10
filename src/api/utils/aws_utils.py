"""AWS Utils."""
# Standard Python Libraries
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import uuid

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


class S3(AWS):
    """S3."""

    def __init__(self):
        """Create S3 Client."""
        self.client = self.get_client("s3")
        self.image_bucket = os.environ.get("AWS_S3_IMAGE_BUCKET")

    def upload_fileobj_image(self, data):
        """Upload fileobject to s3."""
        key = f"{uuid.uuid4().hex}.png"
        self.client.upload_fileobj(data, self.image_bucket, key)
        host = "https://s3.amazonaws.com"
        url = f"{host}/{self.image_bucket}/{key}"

        return key, self.image_bucket, url


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
        """Init."""
        self.client = self.get_client("cognito-idp")

    def get_user_groups(self, username: str):
        """Get groups for user."""
        return self.client.admin_list_groups_for_user(
            Username=username, UserPoolId=COGNITO_USER_POOL_ID, Limit=50
        )

    def get_user(self, username, return_email: bool = False):
        """Get user from cognito."""
        user = self.client.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )
        if return_email:
            return self.get_email_from_user(user)
        return user

    def list_users(self, return_emails: bool = False):
        """List users in cognito."""
        users = self.client.list_users(UserPoolId=COGNITO_USER_POOL_ID)["Users"]
        if return_emails:
            return self.get_emails_from_users(users)
        return users

    def disable_user(self, username):
        """Disable user in cognito."""
        return self.client.admin_disable_user(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )

    def delete_user(self, username):
        """Delete user from cognito."""
        self.disable_user(username)
        return self.client.admin_delete_user(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )

    def enable_user(self, username):
        """Enable user in cognito."""
        return self.client.admin_enable_user(
            UserPoolId=COGNITO_USER_POOL_ID, Username=username
        )

    def confirm_user(self, username):
        """Confirm user in cognito."""
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

    def get_email_from_user(self, user):
        """Get email address for user returned by cognito or database."""
        key = "UserAttributes" if "UserAttributes" in user else "Attributes"
        return next(filter(lambda x: x["Name"] == "email", user[key]), {}).get("Value")

    def get_emails_from_users(self, users):
        """Get emails from a list of users from cognito or database."""
        emails = []
        for user in users:
            email = self.get_email_from_user(user)
            if email:
                emails.append(email)
        return emails
