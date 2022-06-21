from django.template.defaultfilters import lower
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from services.api.v1.serializers import PickDropSerializer
from rest_framework.views import APIView
from users.api.v1.serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from services.models import RiderRequest, DriverAcceptedRequest
from services.api.v1.serializers import RiderRequestSerializer, DriverAcceptCancelRideSerializer

User = get_user_model()


class PickDropView(APIView):
    serializer_class = PickDropSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            local_drivers = []
            pick = lower(serializer.validated_data["pick"])
            drivers = User.objects.filter(account_type="drive_and_deliver")
            for driver in drivers:
                if lower(driver.city) in pick:
                    busy_driver = RiderRequest.objects.filter(status="1", deriver=driver).first()
                    if busy_driver:
                        continue
                    drivers_data = UserProfileSerializer(driver, many=False)
                    local_drivers.append(drivers_data.data)
            return Response({'drivers': local_drivers}, status=status.HTTP_200_OK)
        return Response({'error': "there is error"}, status=status.HTTP_400_BAD_REQUEST)


class RiderRequestView(APIView):
    serializer_class = RiderRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            requester = serializer.validated_data["requester"]
            deriver = serializer.validated_data["deriver"]
            obj = RiderRequest.objects.filter(requester=requester, deriver=deriver).first()
            if obj is None:
                serializer.save()
                return Response({"response": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"response": "You have already made request to that Driver"})
        return Response({"response": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RideRequestView(APIView):
    serializer_class = RiderRequestSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        if user.account_type == "drive_and_deliver":
            made_request = RiderRequest.objects.filter(deriver_id=user.id, status="0")
            serializer = self.serializer_class(made_request, many=True)
            return Response({"response": serializer.data}, status=status.HTTP_200_OK)
        elif user.account_type == "rider":
            made_request = RiderRequest.objects.filter(requester_id=user.id, status="0")
            serializer = self.serializer_class(made_request, many=True)
            return Response({"response": serializer.data}, status=status.HTTP_200_OK)
        return Response({"response": "This is not valid User Id"}, status=status.HTTP_400_BAD_REQUEST)


class RequesterCancelRideView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id is not None:
            try:
                cancel_ride = RiderRequest.objects.get(id=id)
                if cancel_ride.id:
                    ride_id = cancel_ride.id
                    cancel_ride.delete()
                    return Response({"response": f"Your ride ID NO:{ride_id} has been cancel successfully!"})
            except:
                return Response({"response": "We can not find any Ride for canceling."})
        return Response({"response": "Please Provide the ID of Ride, which you want to cancel."})


class DriverCancelAcceptRideView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DriverAcceptCancelRideSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            id = serializer.validated_data["request_id"]
            status_request = serializer.validated_data["status"]
            if status_request == "0":
                ride_request = RiderRequest.objects.filter(id=id).first()
                if ride_request is not None:
                    ride_request.delete()
                    return Response({"response": "Request for ride is canceled successfully!"},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"response": "Request is already canceled!"}, status=status.HTTP_400_BAD_REQUEST)
            if status_request == "1":
                ride_request = RiderRequest.objects.filter(id=id).first()
                if ride_request is not None:
                    requester = ride_request.requester
                    driver = ride_request.deriver
                    accepted_request = DriverAcceptedRequest(requester=requester, driver=driver,
                                                             rider_request=ride_request)
                    accepted_request.save()
                    ride_request.status = 1
                    ride_request.save()
                    serializer_ride_request = RiderRequestSerializer(ride_request, many=False)
                    return Response({"response": serializer_ride_request.data}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({"response": "There is no any request of that ID."},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"response": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RideSuccessfulView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        ride_succeeded = RiderRequest.objects.filter(id=id).first()
        if ride_succeeded is not None:
            ride_succeeded.delete()
            return Response({"response": "Thank You For Using Uber Demo Services"})
        return Response({"response": "This ID is not Exist"})


class AcceptedRidesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RiderRequestSerializer

    def get(self, request, id):
        if id is not None:
            user = User.objects.get(id=id)
            if user.account_type == "drive_and_deliver":
                made_request = RiderRequest.objects.filter(deriver_id=user.id, status="1")
                serializer = self.serializer_class(made_request, many=True)
                return Response({"response": serializer.data}, status=status.HTTP_200_OK)
            elif user.account_type == "rider":
                made_request = RiderRequest.objects.filter(requester_id=user.id, status="1")
                serializer = self.serializer_class(made_request, many=True)
                return Response({"response": serializer.data}, status=status.HTTP_200_OK)
            return Response({"response": "This is not valid User Id"}, status=status.HTTP_400_BAD_REQUEST)
