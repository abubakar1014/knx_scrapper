# Generated by Django 3.0 on 2024-02-25 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0006_scraperdetail'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='profiledata',
            unique_together={('address', 'phone_number')},
        ),
    ]
