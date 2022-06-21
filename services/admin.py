from django.contrib import admin
from services.models import RiderRequest, DriverAcceptedRequest


@admin.register(RiderRequest)
class RiderRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'destination_label', 'pickup_label', 'destination_coordinates', 'pickup_coordinates',
                    'status', 'requester', 'deriver', 'updated_at', 'created_at']


@admin.register(DriverAcceptedRequest)
class DriverAcceptedRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'requester', 'driver', 'rider_request', 'created_at']
