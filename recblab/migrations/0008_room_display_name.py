# Generated by Django 3.2.14 on 2022-08-18 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recblab', '0007_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='display_name',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]