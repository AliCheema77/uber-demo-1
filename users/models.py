from django.contrib.auth.models import AbstractUser
import random
import string
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created


def get_random_str(l):
    ran = ''.join(random.choices("{0}{1}".format(string.ascii_uppercase, string.digits), k=l))
    return ran


class User(AbstractUser):
    ACCOUNT_TYPE = (
        ('drive_and_deliver', 'Drive And Deliver'),
        ('rider', 'Rider'),
    )
    VEHICLE_CHOICES = (
        ('ubermini', 'uberMINI'),
        ('uberauto', 'uberAUTO'),
        ('ubermoto', 'uberMOTO')
    )
    phone_number = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    invite_code = models.CharField(max_length=50, null=True, blank=True)
    vehicle = models.CharField(choices=VEHICLE_CHOICES, max_length=100, null=True, blank=True)
    partner_photo = models.ImageField(upload_to="user_detail/")
    vehicle_registration_book = models.ImageField(upload_to="user_detail/", null=True, blank=True)
    driving_licence_front_side = models.ImageField(upload_to="user_detail/", null=True, blank=True)
    account_type = models.CharField(choices=ACCOUNT_TYPE, max_length=100)

    terms_and_conditions = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # send an e-mail to the user
    context = {
        'username': reset_password_token.user.get_full_name,
        'reset_password_token': reset_password_token.key
    }
    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)
    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Port Pass App"),
        # message:
        email_plaintext_message,
        # from:
        settings.DEFAULT_FROM_EMAIL,
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


class UserSignupCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = "9- User Code"
