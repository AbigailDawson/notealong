# Generated by Django 5.0 on 2024-01-09 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0010_remove_profile_collections_saved_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='collections_saved',
            field=models.ManyToManyField(default='', to='main_app.collection'),
        ),
    ]