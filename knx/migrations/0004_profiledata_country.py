# Generated by Django 3.0 on 2024-02-09 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0003_profiledata_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='profiledata',
            name='country',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
