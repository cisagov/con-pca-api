from rest_framework.views import APIView
from rest_framework.response import Response
import boto3


class WebsiteListView(APIView):
    def get(self, request):
        s3 = boto3.client("s3")
        resp = s3.list_objects(Bucket="con-pca-stage-websites", Delimiter="/")
        return Response([o.get("Prefix") for o in resp.get("CommonPrefixes")])
