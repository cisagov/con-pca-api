"""
Testing Email Views.

"""
# Standard Python Libraries
import logging
import json

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
        logger.info("starting the post")
        sp = request.data.copy()
        logger.info(sp)
        # build the template
        # send the test
        # tear the template down
        sent_template = None
        try:
            logger.info("in the try if and about to check for template")
            if sp.get("template").get("name"):
                tmp_template = sp.get("template")
                tmp_template["html"] = str(tmp_template["html"]).replace(
                    "<%URL%>", "{{.URL}}"
                )
                sent_template = campaign_manager.generate_email_template(
                    tmp_template.get("name") + "_test",
                    tmp_template.get("html"),
                    tmp_template.get("subject"),
                    tmp_template.get("text"),
                )
            else:
                logger.info("name check came back false(Taking default)")

            test_send = self.build_test_smtp(sp)
            test_response = campaign_manager.send_test_email(test_send)
        finally:
            logger.info("finished the email test send")
            if sent_template:
                logger.info(sent_template)
                campaign_manager.delete_email_template(sent_template.id)

        return Response(test_response)

    # def cleanup(self, template_name)
    #     """get all the templates find the one with the name we have and delete it by id"""

    def build_test_smtp(self, sp):
        logger.info("attempting to get the smtp")
        smtp = sp.get("smtp")
        if sp.get("template").get("name"):
            template = sp.get("template")
            template["name"] = template["name"] + "_test"
        else:
            template = {"name": sp.get("template").get("name")}

        logger.info("attempting to to build the smtp _test object")
        smtp_test = {
            "template": template,
            "first_name": sp.get("first_name"),
            "last_name": sp.get("last_name"),
            "email": sp.get("email"),
            "position": sp.get("position"),
            "url": "https://www.google.com",
            "smtp": {
                "from_address": smtp.get("from_address"),
                "host": smtp.get("host"),
                "username": smtp.get("username"),
                "password": smtp.get("password"),
                "ignore_cert_errors": smtp.get("ignore_cert_errors"),
                "headers": smtp.get("headers"),
            },
        }
        logger.info("returning smtp")
        logger.info(json.dumps(smtp_test))
        return smtp_test
