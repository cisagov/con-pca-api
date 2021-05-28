"""User Views."""
# Third-Party Libraries
from rest_framework.response import Response
from rest_framework.views import APIView

# cisagov Libraries
from api.utils.aws_utils import Cognito

cognito = Cognito()


class UsersView(APIView):
    """UsersView."""

    def get(self, request):
        """Get."""
        return Response(cognito.list_users())


class UserView(APIView):
    """UserView."""

    def delete(self, request, username):
        """Delete."""
        return Response(cognito.delete_user(username))


class UserConfirmView(APIView):
    """UserConfirmView."""

    def get(self, request, username):
        """Get."""
        return Response(cognito.confirm_user(username))
