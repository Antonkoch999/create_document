# Generated by Django 3.1.3 on 2020-11-30 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generate_docx', '0002_client_address_of_bank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='address_of_bank',
            field=models.TextField(),
        ),
    ]
