from django.views.generic import ListView
from .models import Booking


class BookingListView(ListView):
    model = Booking
