# Generated by Django 3.0 on 2024-02-17 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0004_profiledata_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiledata',
            name='company_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
