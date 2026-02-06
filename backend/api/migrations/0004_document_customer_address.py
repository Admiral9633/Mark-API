# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_invoice_data_extraction'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='customer_address',
            field=models.TextField(blank=True, help_text='Kundenadresse', null=True),
        ),
    ]
