# Generated by Django 3.2.14 on 2022-08-14 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recblab', '0004_user_display_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]
