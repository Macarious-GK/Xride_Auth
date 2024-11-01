# Generated by Django 5.1.2 on 2024-11-01 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth_V0', '0003_alter_xrideuser_licence_photo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xrideuser',
            name='licence_photo',
            field=models.ImageField(blank=True, null=True, upload_to='media/licence/'),
        ),
        migrations.AlterField(
            model_name='xrideuser',
            name='national_id_photo',
            field=models.ImageField(blank=True, null=True, upload_to='media/national_id/'),
        ),
        migrations.AlterField(
            model_name='xrideuser',
            name='personal_photo',
            field=models.ImageField(blank=True, null=True, upload_to='media/personal/'),
        ),
    ]
