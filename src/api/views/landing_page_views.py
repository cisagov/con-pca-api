"""LandingPage Views."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.manager import CampaignManager
from api.serializers.landing_page_serializers import LandingPageQuerySerializer
from api.services import LandingPageService, SubscriptionService

campaign_manager = CampaignManager()

subscription_service = SubscriptionService()
landing_page_service = LandingPageService()


class LandingPagesListView(APIView):
    """LandingPagesListView."""

    def get(self, request):
        """Get method."""
        serializer = LandingPageQuerySerializer(request.GET.dict())
        parameters = serializer.data

        with_default = False
        if request.query_params:
            if request.query_params["with_default"]:
                with_default = True

        if not parameters:
            parameters = request.data.copy()

        parameters.pop("is_default_template")
        landing_page_list = landing_page_service.get_list(parameters)

        for landing_page in landing_page_list:
            if landing_page["is_default_template"]:
                default_landing_page = landing_page.copy()
                default_landing_page["name"] = (
                    "(System Default)" + default_landing_page["name"]
                )
                default_landing_page["landing_page_uuid"] = 0

                if with_default:
                    landing_page_list.append(default_landing_page)
                break

        return Response(landing_page_list, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()
        if landing_page_service.exists({"name": post_data["name"]}):
            return Response(
                {"error": "LandingPage with name already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        landing_page = campaign_manager.create_landing_page(
            name=post_data["name"], template=post_data["html"]
        )

        post_data["gophish_template_id"] = landing_page.id

        created_response = landing_page_service.save(post_data)

        if post_data["is_default_template"]:
            landing_page_service.clear_and_set_default(
                created_response["landing_page_uuid"]
            )

        return Response(created_response, status=status.HTTP_201_CREATED)


class LandingPageView(APIView):
    """LandingPageView."""

    def get(self, request, landing_page_uuid):
        """Get method."""
        landing_page = landing_page_service.get(landing_page_uuid)
        return Response(landing_page)

    def patch(self, request, landing_page_uuid):
        """Patch method."""
        data = request.data.copy()

        landing_page = landing_page_service.get(landing_page_uuid)

        campaign_manager.put_landing_page(
            gp_id=landing_page["gophish_template_id"],
            name=data["name"],
            html=data["html"],
        )

        if data["is_default_template"]:
            landing_page_service.clear_and_set_default(landing_page_uuid)

        # this really seems like there should be a better way.
        update_put_value = {
            "landing_page_uuid": landing_page_uuid,
            "name": data["name"],
            "is_default_template": data["is_default_template"],
            "html": data["html"],
        }
        updated_response = landing_page_service.update(
            landing_page_uuid, update_put_value
        )
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, landing_page_uuid):
        """Delete method."""
        landing_page = landing_page_service.get(
            landing_page_uuid, fields=["landing_page_uuid", "gophish_template_id"]
        )
        delete_response = landing_page_service.delete(landing_page["landing_page_uuid"])
        campaign_manager.delete_landing_page(landing_page["gophish_template_id"])
        return Response(delete_response, status=status.HTTP_200_OK)
