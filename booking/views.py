from datetime import date, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
from django.views.generic import ListView, TemplateView, DetailView
from os import unlink
from templated_docs import fill_template
from .models import Booking, BookingItem, Agreement


class HomeView(TemplateView):
    template_name = 'booking/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        potential_incomes = [item.total() for item in BookingItem.objects.filter(booking__state__income=1)]
        context['potentiel_income'] = sum(filter(bool, potential_incomes))
        confirmed_incomes = [item.total() for item in BookingItem.objects.filter(booking__state__income__in=(2, 3))]
        context['confirmed_income'] = sum(filter(bool, confirmed_incomes))
        context['total_income'] = context['potentiel_income'] + context['confirmed_income']
        return context


class BookingListView(ListView):
    queryset = Booking.objects.order_by('title')


class BookingDetailView(DetailView):
    model = Booking


class CreateAgreementView(LoginRequiredMixin, DetailView):
    model = Booking

    def render_to_response(self, context, **response_kwargs):
        year = self.object.items.earliest('begin').begin.year
        try:
            order = Agreement.objects.filter(date__year=year).latest('order').order + 1
        except Agreement.DoesNotExist:
            order = 1
        agreement = Agreement.objects.create(date=now().date(), order=order)
        self.object.agreement = agreement
        self.object.save()
        context['agreement'] = agreement
        for ext in ('odt', 'pdf'):
            filename = fill_template('booking/agreement.odt', context, output_format=ext)
            visible_filename = "Convention_{number}_{title}.{ext}".format(number=agreement.number(), ext=ext,
                                                                          title=slugify(self.object.title))
            f = open(filename, 'rb')
            getattr(agreement, ext).save(visible_filename, File(f))
            f.close()
            unlink(filename)
        return HttpResponseRedirect(reverse('booking:booking_list'))


class OccupancyView(TemplateView):
    template_name = 'booking/occupancy.html'

    def occupancy_for(self, day, product):
        items = BookingItem.objects.filter(begin__lte=day, end__gt=day, product=product)
        items = items.filter(booking__state__income__in=(1, 2, 3), headcount__isnull=False)
        items = items.order_by('booking__title')
        items = items.values('booking__title')
        items = items.annotate(headcount=Sum('headcount'))
        return (sum([item['headcount'] for item in items]), items)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        occupancy = []
        for i in range(365):
            day = date(2017, 1, 1) + timedelta(days=i)
            occupancy.append((day, ) + self.occupancy_for(day, 2) + self.occupancy_for(day, 1))
        context['occupancy'] = occupancy
        return context
