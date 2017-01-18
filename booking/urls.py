from django.conf.urls import url, include
from .views import BookingListView, BookingDetailView, OccupancyView


urlpatterns = [
    url(r'^booking/$', BookingListView.as_view()),
    url(r'^booking/(?P<pk>\d+)/$', BookingDetailView.as_view(), name='booking_detail'),
    url(r'^occupancy/$', OccupancyView.as_view()),
]
