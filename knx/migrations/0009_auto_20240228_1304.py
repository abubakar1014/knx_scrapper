# Generated by Django 3.0 on 2024-02-28 13:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0008_auto_20240228_1258'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='scraperdetail',
            unique_together={('country_name', 'url')},
        ),
    ]