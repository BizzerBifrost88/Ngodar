# Generated by Django 5.1.2 on 2024-11-15 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngodars', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='premise',
            name='premisetype',
            field=models.TextField(choices=[('hotel', 'Hotel'), ('Catering', 'catering'), ('Food', 'food')], default=None),
        ),
    ]
