# Generated by Django 5.1.2 on 2024-11-02 09:58

import django.db.models.deletion
import ngodars.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MERCHANT',
            fields=[
                ('merchantID', models.AutoField(primary_key=True, serialize=False)),
                ('merchantname', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='USER',
            fields=[
                ('userID', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('password', models.TextField()),
                ('phone', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ADDRESS',
            fields=[
                ('addressID', models.AutoField(primary_key=True, serialize=False)),
                ('fullname', models.TextField()),
                ('statearea', models.TextField()),
                ('poscode', models.TextField()),
                ('unit', models.TextField(default=None)),
                ('streetname', models.TextField()),
                ('merchantID', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ngodars.merchant')),
                ('userID', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ngodars.user')),
            ],
        ),
        migrations.CreateModel(
            name='PREMISE',
            fields=[
                ('premiseID', models.AutoField(primary_key=True, serialize=False)),
                ('premisename', models.TextField()),
                ('premiseimage', models.ImageField(upload_to='premise_images/', validators=[ngodars.models.PREMISE.validate_image])),
                ('addressID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ngodars.address')),
                ('merchantID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ngodars.merchant')),
            ],
        ),
        migrations.CreateModel(
            name='ITEM',
            fields=[
                ('itemID', models.AutoField(primary_key=True, serialize=False)),
                ('itemname', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('itemimage', models.ImageField(upload_to='item_images/', validators=[ngodars.models.ITEM.validate_image])),
                ('premiseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ngodars.premise')),
            ],
        ),
        migrations.AddField(
            model_name='merchant',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ngodars.user'),
        ),
        migrations.CreateModel(
            name='BOOKING',
            fields=[
                ('bookingID', models.AutoField(primary_key=True, serialize=False)),
                ('payment', models.TextField(choices=[('not pay', 'Not Pay'), ('paid', 'Paid')], default='not pay')),
                ('datetime', models.DateTimeField()),
                ('itemID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ngodars.item')),
                ('userID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ngodars.user')),
            ],
        ),
    ]
