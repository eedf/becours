from django.conf.urls import url, include
from .views import BookingListView


urlpatterns = [
    url(r'^$', BookingListView.as_view()),
]
