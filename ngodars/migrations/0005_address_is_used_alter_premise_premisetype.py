# Generated by Django 5.1.2 on 2024-11-19 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngodars', '0004_alter_address_fullname_alter_address_poscode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='premise',
            name='premisetype',
            field=models.TextField(choices=[('Hall', 'hall'), ('Catering', 'catering'), ('Food', 'food')], default=None),
        ),
    ]
