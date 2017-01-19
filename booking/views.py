from datetime import date, timedelta
from django.views.generic import ListView, TemplateView
from .models import Booking, BookingItem


class BookingListView(ListView):
    model = Booking


class OccupancyView(TemplateView):
    template_name = 'booking/occupancy.html'

    def occupancy_for(self, day):
        items = BookingItem.objects.filter(begin__lte=day, end__gt=day, product=1, headcount__isnull=False)
        items = items.order_by('headcount', 'booking__title')
        return (sum([item.headcount for item in items]), items)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        occupancy = []
        for i in range(365):
            day = date(2017, 1, 1) + timedelta(days=i)
            occupancy.append((day, ) + self.occupancy_for(day))
        context['occupancy'] = occupancy
        return context
