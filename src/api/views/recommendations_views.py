"""
Recommendation Views.

This handles the api for all the Template urls.
"""
# Third-Party Libraries
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Local Libraries
from api.serializers.recommendations_serializers import (
    RecommendationsPostSerializer,
    RecommendationsQuerySerializer,
    RecommendationsPatchSerializer,
)

from api.services import RecommendationService

recommendation_service = RecommendationService()


class RecommendationsListView(APIView):
    """
    This is the Recommendations List API View.

    This handles the API to get a List of Recommendations.
    """

    @swagger_auto_schema(
        query_serializer=RecommendationsQuerySerializer,
        operation_id="List of Recommendations",
    )
    def get(self, request):
        """Get method."""
        serializer = RecommendationsQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()
        recommendations_list = recommendation_service.get_list(parameters)
        return Response(recommendations_list, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=RecommendationsPostSerializer,
        operation_id="Create Recommendations",
    )
    def post(self, request, format=None):
        """Post method."""
        post_data = request.data.copy()

        if recommendation_service.exists({"name": post_data["name"]}):
            return Response(
                {"error": "Recommendation with name already exists"},
                status=status.HTTP_409_CONFLICT,
            )
        created_response = recommendation_service.save(post_data)

        if "errors" in created_response:
            return Response(created_response, status=status.HTTP_400_BAD_REQUEST)
        return Response(created_response, status=status.HTTP_201_CREATED)


class RecommendationsView(APIView):
    """
    This is the Recommendations API View.

    This handles the API for a Recommendation with recommendations_uuid.
    """

    @swagger_auto_schema(operation_id="Get a single Recommendation")
    def get(self, request, recommendations_uuid):
        """Get method."""
        recommendations = recommendation_service.get(recommendations_uuid)
        return Response(recommendations)

    @swagger_auto_schema(
        request_body=RecommendationsPatchSerializer,
        operation_id="Update and Patch single Recommendation",
    )
    def patch(self, request, recommendations_uuid):
        """Patch method."""
        put_data = request.data.copy()
        updated_response = recommendation_service.update(recommendations_uuid, put_data)
        if "errors" in updated_response:
            return Response(updated_response, status=status.HTTP_400_BAD_REQUEST)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(operation_id="Delete single Recommendation")
    def delete(self, request, recommendations_uuid):
        """Delete method."""
        delete_response = recommendation_service.delete(recommendations_uuid)
        if "errors" in delete_response:
            return Response(delete_response, status=status.HTTP_400_BAD_REQUEST)
        return Response(delete_response, status=status.HTTP_200_OK)
