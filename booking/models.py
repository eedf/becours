from cuser.middleware import CuserMiddleware
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import now
from math import floor


class TrackingEvent(models.Model):
    ADD = 1
    CHANGE = 2
    DELETE = 3
    OPERATION_CHOICES = (
        (ADD, "Ajout"),
        (CHANGE, "Modification"),
        (DELETE, "Suppression"),
    )
    operation = models.IntegerField(verbose_name="Opération", choices=OPERATION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Utilisateur", blank=True, null=True,
                             related_name="tracking_events", on_delete=models.PROTECT)
    date = models.DateTimeField()
    obj_ct = models.ForeignKey(ContentType, related_name='log_entries', on_delete=models.PROTECT)
    obj_pk = models.PositiveIntegerField()
    obj = GenericForeignKey('obj_ct', 'obj_pk')

    class Meta:
        verbose_name = "Événement"


class TrackingValue(models.Model):
    event = models.ForeignKey(TrackingEvent, verbose_name="Événement")
    field = models.CharField(max_length=100, verbose_name="Champ")
    value = models.TextField(null=True, verbose_name="Valeur")

    class Meta:
        verbose_name = "Valeur"


class TrackingMixin(object):
    def save(self, *args, **kwargs):
        change = bool(self.pk)
        if change:
            old = self.__class__.objects.get(pk=self.pk)
        super().save(*args, **kwargs)
        event = TrackingEvent.objects.create(
            operation=TrackingEvent.CHANGE if self.pk else TrackingEvent.ADD,
            user=CuserMiddleware.get_user(),
            date=now(),
            obj=self,
        )
        for field in self._meta.fields:
            if field.name == 'id':
                continue
            value = getattr(self, field.name)
            if not change and value is not None and value != "" or change and value != getattr(old, field.name):
                TrackingValue.objects.create(
                    event=event,
                    field=field.name,
                    value=str(value)
                )

    def delete(self, *args, **kwargs):
        TrackingEvent.objects.create(
            operation=TrackingEvent.DELETE,
            user=CuserMiddleware.get_user(),
            date=now(),
            obj=self,
        )
        super().delete(*args, **kwargs)


class Agreement(models.Model):
    date = models.DateField(verbose_name="Date")
    order = models.IntegerField(verbose_name="Numéro d'ordre")
    odt = models.FileField(upload_to='conventions', blank=True)
    pdf = models.FileField(upload_to='conventions', blank=True)

    class Meta:
        verbose_name = "Convention"

    def number(self):
        return "{year}-{order:03}".format(year=self.date.year, order=self.order)
    number.short_description = "Numéro"

    def __str__(self):
        return self.number()


class BookingState(models.Model):
    INCOME_CHOICES = (
        (1, "Potentiel"),
        (2, "Confirmé"),
        (3, "Facturé"),
        (4, "Infirmé"),
        (5, "Annulé"),
    )
    title = models.CharField(verbose_name="Intitulé", max_length=100)
    income = models.IntegerField(verbose_name="Chiffre d'affaire", choices=INCOME_CHOICES)

    class Meta:
        verbose_name = "Statut"
        ordering = ('title', )

    def __str__(self):
        return self.title


class Booking(TrackingMixin, models.Model):
    ORG_TYPE_CHOICES = (
        (1, "EEDF"),
        (2, "Scouts français"),
        (3, "Scouts étrangers"),
        (4, "Association"),
        (5, "Particulier"),
        (6, "Scolaires"),
    )
    title = models.CharField(verbose_name="Intitulé", max_length=100, blank=True)
    org_type = models.IntegerField(verbose_name="Type d'organisation", choices=ORG_TYPE_CHOICES, blank=True, null=True)
    contact = models.CharField(verbose_name="Contact", max_length=100, blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)
    tel = models.CharField(verbose_name="Téléphone", max_length=12, blank=True)
    state = models.ForeignKey(BookingState, verbose_name="Statut", blank=True, null=True)
    description = models.TextField(verbose_name="Description", blank=True)
    agreement = models.OneToOneField(Agreement, verbose_name="Convention", blank=True, null=True, related_name='booking')

    class Meta:
        verbose_name = "Réservation"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('booking:booking_detail', kwargs={'pk': self.pk})

    def begin(self):
        return min(self.items.values_list('begin', flat=True), default=None)

    def end(self):
        return max(self.items.values_list('end', flat=True), default=None)

    def nights(self):
        begin = self.begin()
        end = self.end()
        return begin and end and (end - begin).days

    def headcount(self):
        return sum([item.headcount for item in self.items.all() if item.headcount]) or None

    def overnights(self):
        return sum([item.overnights() for item in self.items.all() if item.overnights()]) or None

    def total(self):
        return sum([item.total() for item in self.items.all() if item.total()]) or None

    def deposit(self):
        total = self.total()
        return total and floor(total * Decimal('0.3'))

    def payment(self):
        return sum(self.payments.values_list('amount', flat=True)) or None

    def balance(self):
        total = self.total()
        payment = self.payment()
        return total and payment and total - payment


class BookingItem(TrackingMixin, models.Model):
    PRODUCT_CHOICES = (
        (1, "Hébergement Terrain"),
        (2, "Hébergement Hameau"),
        (3, "Location matériel"),
        (4, "Refacturation"),
        (5, "Salles"),
    )
    title = models.CharField(verbose_name="Intitulé", max_length=100, blank=True)
    booking = models.ForeignKey(Booking, related_name='items', on_delete=models.CASCADE)
    headcount = models.PositiveIntegerField(verbose_name="Effectif", blank=True, null=True)
    begin = models.DateField(verbose_name="Date de début", blank=True, null=True)
    end = models.DateField(verbose_name="Date de fin", blank=True, null=True)
    product = models.IntegerField(verbose_name="Produit", choices=PRODUCT_CHOICES)
    price_pppn = models.DecimalField(verbose_name="Prix/nuitée", max_digits=8, decimal_places=2, null=True, blank=True)
    price_pn = models.DecimalField(verbose_name="Prix/nuit", max_digits=8, decimal_places=2, null=True, blank=True)
    price_pp = models.DecimalField(verbose_name="Prix/pers", max_digits=8, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(verbose_name="Prix forfait", max_digits=8, decimal_places=2, null=True, blank=True)
    cotisation = models.BooleanField(verbose_name="Cotis° associé", default=True)

    def __str__(self):
        return self.title or self.get_product_display()

    def nights(self):
        return self.begin and self.end and (self.end - self.begin).days

    def overnights(self):
        nights = self.nights()
        return nights and self.headcount and nights * self.headcount

    def total(self):
        euros = self.price or 0
        nights = self.nights()
        overnights = self.overnights()
        if overnights and self.price_pppn:
            euros += overnights * self.price_pppn
        if nights and self.price_pn:
            euros += nights * self.price_pn
        if self.headcount and self.price_pp:
            euros += self.headcount * self.price_pp
        if self.cotisation and overnights:
            euros += overnights
        return euros or None


class Payment(models.Model):
    MEAN_CHOICES = (
        (1, "Chèque"),
        (2, "Virement"),
        (3, "Espèces"),
    )
    mean = models.IntegerField(verbose_name="Moyen de paiement", choices=MEAN_CHOICES)
    date = models.DateField()
    amount = models.DecimalField(verbose_name="Montant", max_digits=8, decimal_places=2)
    booking = models.ForeignKey(Booking, related_name='payments', on_delete=models.CASCADE)

