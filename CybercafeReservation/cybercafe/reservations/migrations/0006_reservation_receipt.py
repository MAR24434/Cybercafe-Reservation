# Generated by Django 5.0.2 on 2024-10-15 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_remove_pcrental_service_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='receipt',
            field=models.FileField(blank=True, null=True, upload_to='receipts/'),
        ),
    ]
