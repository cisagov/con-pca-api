"""
Image Views.

This handles the api for all the Image urls.
"""
# Standard Python Libraries
import logging

# Third-Party Libraries
from api.utils.aws_utils import S3
from botocore.exceptions import ClientError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class ImageView(APIView):
    """
    This is the ImageView APIView.

    This handles the API for managing images.
    """

    @swagger_auto_schema(
        responses={"200": "Image OK", "400": "Bad Request"},
        security=[],
        operation_id="Single Image",
        operation_description="This handles the operation to upload a single image",
    )
    def post(self, request, format=None):
        """Post method."""
        s3 = S3()

        try:
            image = request.data["file"]
            key, bucket, url = s3.upload_fileobj_image(request.data["file"],)
        except ClientError as e:
            logger.exception(e)
            resp = {"status": "false", "error": str(e), "msg": "Image Upload Failure"}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "status": "true",
            "bucket": bucket,
            "key": key,
            "msg": "Image Upload Successful",
            "imageUrl": url,
        }

        return Response(result, status=status.HTTP_201_CREATED)