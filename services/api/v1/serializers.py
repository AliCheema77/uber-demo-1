from rest_framework import serializers
from services.models import RiderRequest
from users.api.v1.serializers import UserProfileSerializer


class PickDropSerializer(serializers.Serializer):
    pick = serializers.CharField(max_length=255, required=True)
    destination = serializers.CharField(max_length=255, required=True)


class RiderRequestSerializer(serializers.ModelSerializer):
    requester = UserProfileSerializer(many=False, read_only=True)
    deriver = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = RiderRequest
        fields = ['id', 'destination_label', 'pickup_label', 'destination_coordinates', 'pickup_coordinates',
                  'status', 'requester', 'deriver']

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data["requester"] = {
    #         "id": instance.requester.id,
    #         "first_name": instance.requester.first_name,
    #         "last_name": instance.requester.last_name,
    #         "username": instance.requester.username,
    #         "email": instance.requester.email,
    #         "phone_number": instance.requester.phone_number
    #         }
    #     data["deriver"] = {
    #         "id": instance.deriver.id,
    #         "first_name": instance.deriver.first_name,
    #         "last_name": instance.deriver.last_name,
    #         "username": instance.deriver.username,
    #         "email": instance.deriver.email,
    #         "phone_number": instance.deriver.phone_number
    #         }
    #     return data


class DriverAcceptCancelRideSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(required=True)
    status = serializers.CharField(max_length=5, required=True)
