# Generated by Django 5.1.4 on 2025-03-11 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoplist', '0004_remove_salesession_last_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_manual',
            field=models.BooleanField(default=False),
        ),
    ]
