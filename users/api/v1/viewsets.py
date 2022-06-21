from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from twilio.rest import Client
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from users.api.v1.serializers import (
    SignupSerializer,
    UserSerializer,
    UserProfileSerializer,
    VerifyUserSignupCodeSerializer,
    CustomTokenObtainPairSerializer,
    ResendUserSignupEmailSerializer
)
from users.models import get_random_str, UserSignupCode


User = get_user_model()
# account_sid = settings.ACCOUNT_SID
# auth_token = settings.AUTH_TOKEN
# client = Client(account_sid, auth_token)


class SignupViewSet(ModelViewSet):
    serializer_class = SignupSerializer
    queryset = User.objects.none()
    http_method_names = ["post"]


class UserProfileViewSet(ListCreateAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.none()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(email=request.user.email)
        serializer = self.serializer_class(user, many=False)
        return Response({"user_detail": serializer.data}, status=status.HTTP_200_OK)


class VerifyUserSignupCodeViewSet(ListCreateAPIView):
    serializer_class = VerifyUserSignupCodeSerializer
    queryset = UserSignupCode.objects.none()
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.data.get("code")
        user_code = UserSignupCode.objects.filter(code=code)
        if user_code:
            email = user_code.first().email
            EmailAddress.objects.filter(email__exact=email).update(verified=True)
            user_code.delete()
            user = get_user_model().objects.filter(email__exact=email).first()
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserSerializer(user)
            response = {"key": token.key, "user_detail": user_serializer.data, "message": "Email is verified."}
            return Response(response, status=status.HTTP_200_OK)
        return Response({"response": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)


class ResendSignupUserEmailViewSet(ListCreateAPIView):
    serializer_class = ResendUserSignupEmailSerializer
    queryset = UserSignupCode.objects.none()

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        user_email = EmailAddress.objects.filter(email__exact=email).first()
        if user_email:
            if user_email.verified == False:
                code = get_random_str(6)
                while UserSignupCode.objects.filter(code=code).first():
                    code = get_random_str(6)
                instance = UserSignupCode.objects.filter(email=email).first()
                if instance:
                    instance.code = code
                    instance.save()
                message = f"Your new email verification code is \"{code}\""
                # try:
                #     port = get_pre_signed_s3_url(
                #          f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/img/port.png")
                # except:
                #     port = ""
                html_message = render_to_string("account/email/confirmation.html", {"code": code})
                send_mail(
                    "django backend",
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False
                )
                return Response({"response": "Confirmation email sent."})
            return Response({"response": "User already verified."})
        return Response({"response": "Email does not exist."})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
