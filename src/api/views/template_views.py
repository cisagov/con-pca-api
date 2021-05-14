"""
Template Views.

This handles the api for all the Template urls.
"""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.serializers.template_serializers import (
    TemplateQuerySerializer,
    TemplateStopResponseSerializer,
)
from api.services import (
    CampaignService,
    CustomerService,
    SubscriptionService,
    TagService,
    TemplateService,
)
from api.utils.subscription.actions import stop_subscription
from api.utils.subscription.campaigns import get_campaign_from_address
from api.utils.template.personalize import personalize_template
from api.utils.template.selector import select_templates
from api.utils.template.templates import validate_template

campaign_manager = CampaignManager()

template_service = TemplateService()
subscription_service = SubscriptionService()
campaign_service = CampaignService()
customer_service = CustomerService()
tag_service = TagService()


class TemplatesListView(APIView):
    """This is the TemplatesListView."""

    def get(self, request):
        """Get method."""
        serializer = TemplateQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()

        # Allow querying a list of templates
        templates = request.GET.get("templates")
        if templates:
            parameters["template_uuid"] = {"$in": templates.split(",")}

        template_list = template_service.get_list(parameters)
        return Response(template_list, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()
        if template_service.exists({"name": post_data["name"]}):
            return Response(
                {"error": "Template with name already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        is_invalid = validate_template(post_data)
        if is_invalid:
            return Response(is_invalid, status=status.HTTP_400_BAD_REQUEST)

        created_response = template_service.save(post_data)
        return Response(created_response, status=status.HTTP_201_CREATED)


class TemplateView(APIView):
    """TemplateView."""

    def get(self, request, template_uuid):
        """Get method."""
        template = template_service.get(template_uuid)
        return Response(template)

    def patch(self, request, template_uuid):
        """Patch method."""
        put_data = request.data.copy()
        if put_data["landing_page_uuid"] == "0" or not put_data["landing_page_uuid"]:
            put_data["landing_page_uuid"] = None

        template = template_service.get(template_uuid)
        template.update(put_data)
        is_invalid = validate_template(template)
        if is_invalid:
            return Response(is_invalid, status=status.HTTP_400_BAD_REQUEST)
        updated_response = template_service.update(template_uuid, template)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, template_uuid):
        """Delete method."""
        delete_response = template_service.delete(template_uuid)
        return Response(delete_response, status=status.HTTP_200_OK)


class TemplateStopView(APIView):
    """TemplateStopView."""

    def get(self, request, template_uuid):
        """Get method."""
        # get subscriptions
        campaigns = campaign_service.get_list(
            parameters={"template_uuid": template_uuid},
            fields=["subscription_uuid"],
        )

        subscription_uuids = {c["subscription_uuid"] for c in campaigns}
        updated_subscriptions = []
        for uuid in subscription_uuids:
            subscription = subscription_service.get(uuid)
            if subscription["active"]:
                stop_subscription(subscription)
                updated_subscriptions.append(subscription)

        # Get template
        template = template_service.get(template_uuid)

        # Update template
        template["retired"] = True
        template["retired_description"] = "Manually Stopped"
        template_service.update(template_uuid, template)

        # Generate and return response
        resp = {"template": template, "subscriptions": updated_subscriptions}
        serializer = TemplateStopResponseSerializer(resp)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class SendingTestEmailsView(APIView):
    """SendingTestEmailsView."""

    def post(self, request):
        """Post."""
        sp = request.data.copy()
        # build the template
        # send the test
        # tear the template down
        sent_template = None
        try:
            if sp.get("customer_uuid"):
                customer = customer_service.get(sp["customer_uuid"])
            else:
                customer = customer_service.get_list()[0]
            if sp.get("template").get("name"):
                tmp_template = sp.get("template")
                tmp_template["html"] = str(tmp_template["html"]).replace(
                    "<%URL%>", "{{.URL}}"
                )
                personalized_data = personalize_template(
                    customer_info=customer,
                    template_data=[tmp_template],
                    sub_data=None,
                    tag_list=tag_service.get_list(),
                )[0]
                sent_template = campaign_manager.create_email_template(
                    tmp_template.get("name") + "_test",
                    personalized_data["data"],
                    personalized_data["subject"],
                    tmp_template.get("text"),
                )

                test_send = self._build_test_smtp(sp, personalized_data["from_address"])
            else:
                test_send = self._build_test_smtp(
                    sp, sp.get("smtp").get("from_address")
                )
            test_response = campaign_manager.send_test_email(test_send)
        finally:
            if sent_template:
                campaign_manager.delete_email_template(sent_template.id)

        return Response(test_response)

    def _build_test_smtp(self, sp, from_address):
        smtp = sp.get("smtp")
        if sp.get("template").get("name"):
            template = sp.get("template")
            template["name"] = template["name"] + "_test"
        else:
            template = {"name": sp.get("template").get("name")}

        smtp_test = {
            "template": template,
            "first_name": sp.get("first_name"),
            "last_name": sp.get("last_name"),
            "email": sp.get("email"),
            "position": sp.get("position"),
            "url": "https://www.google.com",
            "smtp": {
                "from_address": get_campaign_from_address(smtp, from_address),
                "host": smtp.get("host"),
                "username": smtp.get("username"),
                "password": smtp.get("password"),
                "ignore_cert_errors": smtp.get("ignore_cert_errors"),
                "headers": smtp.get("headers"),
            },
        }
        return smtp_test


class TemplateEmailImportView(APIView):
    """TemplateEmailImportView."""

    def post(self, request):
        """Post."""
        post_data = request.data.copy()
        return Response(
            campaign_manager.import_email(
                content=post_data["content"],
                convert_link=post_data["convert_link"],
            )
        )


class TemplateSelectView(APIView):
    """TemplateSelectView."""

    def get(self, request):
        """Get."""
        templates = template_service.get_list({"retired": False})
        return Response(select_templates(templates))
