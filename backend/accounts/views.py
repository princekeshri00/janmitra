from rest_framework.response import Response
from rest_framework.views import APIView


class CurrentUserView(APIView):
    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "phone_number": request.user.phone_number,
                "role": request.user.role,
                "preferred_language": request.user.preferred_language,
                "is_verified": request.user.is_verified,
            }
        )