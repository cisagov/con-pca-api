"""Image Views."""
# Third-Party Libraries
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.utils.aws_utils import S3


class ImageView(APIView):
    """ImageView."""

    def post(self, request, format=None):
        """Post method."""
        s3 = S3()
        key, bucket, url = s3.upload_fileobj_image(
            request.data["file"],
        )

        result = {
            "status": "true",
            "bucket": bucket,
            "key": key,
            "msg": "Image Upload Successful",
            "imageUrl": url,
        }

        return Response(result, status=status.HTTP_201_CREATED)
