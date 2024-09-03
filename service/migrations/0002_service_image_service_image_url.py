# Generated by Django 5.1 on 2024-09-03 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='service',
            name='image_url',
            field=models.URLField(blank=True, max_length=1024, null=True),
        ),
    ]
