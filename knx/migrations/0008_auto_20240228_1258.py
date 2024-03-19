# Generated by Django 3.0 on 2024-02-28 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0007_auto_20240225_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='scraperdetail',
            name='country_name',
            field=models.CharField(blank=True, default='N/A', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='scraperdetail',
            name='url',
            field=models.CharField(blank=True, default='N/A', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='scraperdetail',
            name='count',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
