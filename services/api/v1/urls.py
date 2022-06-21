from django.urls import path
from services.api.v1.viewsets import PickDropView, RiderRequestView, RideRequestView, RequesterCancelRideView,\
    DriverCancelAcceptRideView, RideSuccessfulView, AcceptedRidesView


urlpatterns = [
    path('pick_drop/', PickDropView.as_view(), name="pick_drop"),
    path('rider_request/', RiderRequestView.as_view(), name="rider_request"),
    path('requests/', RideRequestView.as_view(), name="request"),
    path('cancel_ride/<int:id>/', RequesterCancelRideView.as_view(), name="cancel_ride"),
    path("cancel_accept_ride/", DriverCancelAcceptRideView.as_view(), name="cancel_accept_ride/"),
    path("ride_status/<int:id>/", RideSuccessfulView.as_view(), name="ride_status"),
    path("accepted_rides/<int:id>/", AcceptedRidesView.as_view(), name="accepted_rides")
]
