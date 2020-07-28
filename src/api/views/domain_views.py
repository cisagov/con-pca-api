# Third-Party Libraries
import boto3
from rest_framework.response import Response
from rest_framework.views import APIView


class WebsiteListView(APIView):
    def get(self, request):
        s3 = boto3.client("s3")
        resp = s3.list_objects(Bucket="con-pca-stage-websites", Delimiter="/")
        return Response([o.get("Prefix") for o in resp.get("CommonPrefixes")])
