"""Image Views."""
# Standard Python Libraries
import base64

# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ImageView(APIView):
    """ImageView."""

    def post(self, request, format=None):
        """Return base64 encode of an image file."""
        base64_encode = base64.b64encode(request.data["file"].read())

        result = {"imageUrl": f"data:image/jpeg;base64,{base64_encode.decode()}"}

        return Response(result, status=status.HTTP_201_CREATED)
