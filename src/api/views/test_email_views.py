"""
Testing Email Views.

"""
# Standard Python Libraries
import logging

# Third-Party Libraries
# Local
from api.manager import CampaignManager
from api.serializers.sendingprofile_serializers import (
    SendingProfilePatchResponseSerializer,
    SendingProfilePatchSerializer,
    SendingProfileSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
# GoPhish API Manager
campaign_manager = CampaignManager()


class SendingTestEmailsView(APIView):
    """
    This is the SendingProfilesListView APIView.
    This handles the API to get a List of Sending Profiles.
    """

    """
    This is the SendingProfileView APIView.
    This handles the API for creating a new Sending Profile.
    http://localhost:3333/api/util/send_test_email
    """

    @swagger_auto_schema(
        request_body=SendingProfilePatchSerializer,
        responses={"202": SendingProfilePatchResponseSerializer, "400": "Bad Request"},
        security=[],
        operation_id="Create Sending Profile",
        operation_description="This handles the API for the Update Sending Profile with uuid.",
    )
    def post(self, request):
        sp = request.data.copy()
        # build the template
        # send the test
        # tear the template down
        try:
            if sp.get("template").get("name"):
                tmp_template = sp.get("template")
                template_response = campaign_manager.generate_email_template(
                    tmp_template.get("name") + "_test",
                    tmp_template.get("html"),
                    tmp_template.get("subject"),
                    tmp_template.get("text"),
                )

            test_send = self.build_test_smtp(sp)
            test_response = campaign_manager.send_test_email(test_send)
        finally:
            logger.info("finished the email test send")
            # campaign_manager.delete_email_template(sp.get("name")+"_test")

        return Response(test_response)

    def build_test_smtp(self, sp):
        smtp = sp.get("smtp")
        if sp.get("template").get("name"):
            template = sp.get("template")
            template["name"] = template["name"] + "_test"
        else:
            template = {"name": sp.get("template").get("name")}

        smpt_test = {
            "template": template,
            "first_name": sp.get("first_name"),
            "last_name": sp.get("last_name"),
            "email": sp.get("email"),
            "position": sp.get("position"),
            "url": "",
            "smtp": {
                "from_address": smtp.get("from_address"),
                "host": smtp.get("host"),
                "username": smtp.get("username"),
                "password": smtp.get("password"),
                "ignore_cert_errors": smtp.get("ignore_cert_errors"),
                "headers": smtp.get("headers"),
            },
        }
        return smpt_test
