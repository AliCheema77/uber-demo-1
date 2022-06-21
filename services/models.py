from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class RiderRequest(models.Model):
    destination_label = models.CharField(max_length=255)
    pickup_label = models.CharField(max_length=255)
    destination_coordinates = models.CharField(max_length=255)
    pickup_coordinates = models.CharField(max_length=255)
    status = models.CharField(max_length=10)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requester_user")
    deriver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deriver_user")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.requester.username

    class Meta:
        verbose_name = "Rider Request"
        verbose_name_plural = "Rider Requests"
        ordering = ["-created_at"]


class DriverAcceptedRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accepted_request")
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="acceptor_driver")
    rider_request = models.ForeignKey(RiderRequest, on_delete=models.CASCADE, related_name="rider_request_object")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.requester.username

    class Meta:
        verbose_name = "Accepted Request"
        verbose_name_plural = "Accepted Requests"
        ordering = ["-created_at"]

