# Generated by Django 3.0 on 2024-02-09 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0002_auto_20240206_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='profiledata',
            name='city',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
