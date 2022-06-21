from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _
from allauth.account import app_settings as allauth_settings
from allauth.account.forms import ResetPasswordForm
from allauth.utils import email_address_exists, generate_unique_username
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email, send_email_confirmation
from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer
from rest_auth.models import TokenModel
from users.models import get_random_str, UserSignupCode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from allauth.account.models import EmailAddress


User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "id",  'first_name', 'last_name', "email", 'city', 'invite_code', 'partner_photo', 'vehicle',
            'vehicle_registration_book', 'driving_licence_front_side', 'phone_number', 'account_type',
            'terms_and_conditions', "password")
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "email": {
                "required": True,
                "allow_blank": False,
            }
        }

    def _get_request(self):
        request = self.context.get("request")
        if (
                request
                and not isinstance(request, HttpRequest)
                and hasattr(request, "_request")
        ):
            request = request._request
        return request

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address.")
                )
        return email

    @transaction.atomic()
    def create(self, validated_data):
        try:
            user = User(
                email=validated_data.get("email"),
                username=generate_unique_username(
                    [validated_data.get("first_name") + validated_data.get("last_name"), "user"]
                ),
            )
            partner_photo = validated_data.get("partner_photo")
            first_name = validated_data.get("first_name")
            last_name = validated_data.get("last_name")
            phone_number = validated_data.get("phone_number")
            vehicle = validated_data.get("vehicle")
            invite_code = validated_data.get("invite_code")
            city = validated_data.get("city")
            vehicle_registration_book = validated_data.get('vehicle_registration_book')
            driving_licence_front_side = validated_data.get('driving_licence_front_side')
            account_type = validated_data.get('account_type')
            terms_and_conditions = validated_data.get('terms_and_conditions')

            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if phone_number:
                user.phone_number = phone_number
            if partner_photo:
                user.partner_photo = partner_photo
            if vehicle:
                user.vehicle = vehicle
            if invite_code:
                user.invite_code = invite_code
            if city:
                user.city = city
            if vehicle_registration_book:
                user.vehicle_registration_book = vehicle_registration_book
            if driving_licence_front_side:
                user.driving_licence_front_side = driving_licence_front_side
            if account_type:
                user.account_type = account_type
            if terms_and_conditions:
                user.terms_and_conditions = terms_and_conditions

            user.set_password(validated_data.get("password"))
            user.save()
            request = self._get_request()
            setup_user_email(request, user, [])
            try:
                self.send_code_email(user)
            except Exception as e:
                raise serializers.ValidationError(
                    _(f"error while sending email {e}")
                )
        except Exception as e:
            raise serializers.ValidationError(
                _(f"error while creating user... {e}")
            )
        return user

    def send_code_email(self, user):
        code = get_random_str(6)
        while UserSignupCode.objects.filter(code=code).exists():
            code = get_random_str(6)
        user_code = UserSignupCode.objects.filter(email=user.email).first()
        if user_code:
            user_code.code = code
            user_code.save()
        else:
            user_code = UserSignupCode.objects.create(email=user.email, code=code)

        message = f'your email verification code is \"{code}\"'
        html_message = render_to_string("account/email/confirmation.html", {"code": code})
        send_mail(
            'uber email confirmation code',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False
        )
        print("send email key.")

    def save(self, request=None):
        """rest_auth passes request so we must override to accept it"""
        return super().save()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", 'username', "email", 'first_name', 'last_name', 'phone_number', 'city', 'invite_code',
                  'vehicle', "partner_photo", 'vehicle_registration_book', 'driving_licence_front_side', 'account_type',
                  'terms_and_conditions', 'created', 'updated']
        extra_kwargs = {
            "email": {
                "read_only": True
            },
        }


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", 'username', "email", 'first_name', 'last_name', 'phone_number', 'city', 'invite_code',
                  'vehicle', "partner_photo", 'vehicle_registration_book', 'driving_licence_front_side', 'account_type',
                  'terms_and_conditions', 'created', 'updated']
        extra_kwargs = {
            "email": {
                "read_only": True
            },
        }


class CustomTokenSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source="user", read_only=True)

    class Meta:
        model = TokenModel
        fields = ('key', "user_detail")


class PasswordSerializer(PasswordResetSerializer):
    """Custom serializer for rest_auth to solve reset password error"""
    password_reset_form_class = ResetPasswordForm


class VerifyUserSignupCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class ResendUserSignupEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        email = attrs.get("email")
        instance = EmailAddress.objects.filter(email=email).first()
        if not instance.verified:
            raise serializers.ValidationError(f"{email} is not verified email!")

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data["user_detail"] = UserSerializer(self.user, many=False, read_only=True).data
        update_last_login(None, self.user)
        return data
