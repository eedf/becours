from django.contrib import admin
from .models import BookingState, Booking, BookingItem, TrackingEvent, TrackingValue, Agreement


@admin.register(BookingState)
class BookingStateAdmin(admin.ModelAdmin):
    list_display = ('title', )


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('number', 'date')


class BookingItemInline(admin.TabularInline):
    model = BookingItem
    fields = ('product', 'title', 'headcount', 'begin', 'end', 'price_pppn', 'price_pn', 'price_pp', 'price', 'cotisation')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    inlines = (BookingItemInline, )
    list_display = ('title', 'state', 'contact', 'email', 'tel')
    list_filter = ('state', )


class TrackingValueInline(admin.TabularInline):
    model = TrackingValue
    fields = ('field', 'value')


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'obj')
    inlines = (TrackingValueInline, )
