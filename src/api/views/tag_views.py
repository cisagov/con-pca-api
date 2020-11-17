"""
Tag Views.

This handles the api for all the Tag urls.
"""
from api.serializers.tag_serializers import TagQuerySerializer
from api.services import TagService
from api.utils.tag.tags import check_tag_format
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

tag_service = TagService()


class TagsView(APIView):
    """
    This is the Tags View APIView.

    This returns all Tags or POST to create a tag.
    """

    def get(self, request):
        """Get method."""
        serializer = TagQuerySerializer(request.GET.dict())
        parameters = serializer.data
        if not parameters:
            parameters = request.data.copy()
        tag_list = tag_service.get_list(parameters)
        return Response(tag_list, status=status.HTTP_200_OK)

    def post(self, request):
        """Post Method."""
        post_data = request.data.copy()

        if not check_tag_format(post_data["tag"]):
            return Response(
                {"error": "incorrect tag format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tag_service.exists({"tag": post_data["tag"]}):
            return Response(
                {"error": "Tag already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        created_response = tag_service.save(post_data)
        return Response(created_response, status=status.HTTP_201_CREATED)


class TagView(APIView):
    """TagView."""

    def get(self, request, tag_uuid):
        """Get method."""
        tag = tag_service.get(tag_uuid)
        return Response(tag)

    def patch(self, request, tag_uuid):
        """Patch method."""
        put_data = request.data.copy()
        updated_response = tag_service.update(tag_uuid, put_data)
        return Response(updated_response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, tag_uuid):
        """Delete method."""
        delete_response = tag_service.delete(tag_uuid)
        return Response(delete_response, status=status.HTTP_200_OK)
