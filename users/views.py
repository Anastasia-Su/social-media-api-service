import base64

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer, LogoutSerializer
from social.models import Profile
from social.permissions import IsLoggedIn


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            user_data = response.data
            user_instance = User.objects.get(pk=user_data["id"])

            profile_data = {
                "first_name": request.data.get("first_name", ""),
                "last_name": request.data.get("last_name", ""),
                "bio": request.data.get("bio", ""),
            }

            Profile.objects.create(user=user_instance, **profile_data)

        return response


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsLoggedIn]
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            RefreshToken(refresh_token).blacklist()
            # print(refresh_token)
            # authorization_header = request.headers.get("Authorization")
            # if authorization_header and authorization_header.startswith("Bearer "):
            #     access_token = authorization_header.split(" ")[1]
                # print("access_tok", access_token)

                # token_record = BlacklistedToken(
                #     token=access_token, blacklisted_at=timezone.now()
                # )
                # token_record = BlacklistToken.objects.create(
                #     token=access_token, blacklisted_at=timezone.now()
                # )
                # token_record.save()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
