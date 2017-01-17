# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-17 22:19
from __future__ import unicode_literals

import booking.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('order', models.IntegerField()),
                ('file', models.FileField(upload_to='conventions')),
            ],
            options={
                'verbose_name': 'Convention',
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Intitulé')),
                ('org_type', models.IntegerField(blank=True, choices=[(1, 'EEDF'), (2, 'Scouts français'), (3, 'Scouts étrangers'), (4, 'Association'), (5, 'Particulier')], null=True, verbose_name="Type d'organisation")),
                ('contact', models.CharField(blank=True, max_length=100, verbose_name='Contact')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('tel', models.CharField(blank=True, max_length=12, verbose_name='Téléphone')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('agreement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='booking.Agreement', verbose_name='Convention')),
            ],
            options={
                'verbose_name': 'Réservation',
            },
            bases=(booking.models.TrackingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BookingItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, verbose_name='Intitulé')),
                ('headcount', models.PositiveIntegerField(blank=True, null=True, verbose_name='Effectif')),
                ('begin', models.DateField(blank=True, null=True, verbose_name='Date de début')),
                ('end', models.DateField(blank=True, null=True, verbose_name='Date de fin')),
                ('product', models.IntegerField(choices=[(1, 'Hébergement Terrain'), (2, 'Hébergement Hameau'), (3, 'Location matériel'), (4, 'Refacturation'), (5, 'Salles')], verbose_name='Produit')),
                ('price_pppn', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Prix/nuitée')),
                ('price_pn', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Prix/nuit')),
                ('price_pp', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Prix/pers')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Prix forfait')),
                ('cotisation', models.BooleanField(default=True, verbose_name='Cotis° associé')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='booking.Booking')),
            ],
            bases=(booking.models.TrackingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BookingState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Intitulé')),
            ],
            options={
                'verbose_name': 'État',
            },
        ),
        migrations.CreateModel(
            name='TrackingEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.IntegerField(choices=[(1, 'Ajout'), (2, 'Modification'), (3, 'Suppression')], verbose_name='Opération')),
                ('date', models.DateTimeField()),
                ('obj_pk', models.PositiveIntegerField()),
                ('obj_ct', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='log_entries', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tracking_events', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name': 'Événement',
            },
        ),
        migrations.CreateModel(
            name='TrackingValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=100, verbose_name='Champ')),
                ('value', models.TextField(null=True, verbose_name='Valeur')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.TrackingEvent', verbose_name='Événement')),
            ],
            options={
                'verbose_name': 'Valeur',
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='booking.BookingState'),
        ),
    ]
