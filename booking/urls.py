from django.conf.urls import url, include
from .views import BookingListView, OccupancyView


urlpatterns = [
    url(r'^$', BookingListView.as_view()),
    url(r'^occupancy/$', OccupancyView.as_view()),
]
