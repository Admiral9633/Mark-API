# Generated migration for invoice data extraction fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_ai_lexoffice_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='invoice_number',
            field=models.CharField(blank=True, help_text='Rechnungsnummer', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='invoice_date',
            field=models.DateField(blank=True, help_text='Rechnungsdatum', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='due_date',
            field=models.DateField(blank=True, help_text='Fälligkeitsdatum', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Gesamtbetrag brutto', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='net_amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Nettobetrag', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='tax_amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Umsatzsteuer', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='currency',
            field=models.CharField(default='EUR', help_text='Währung', max_length=3),
        ),
        migrations.AddField(
            model_name='document',
            name='vendor_name',
            field=models.CharField(blank=True, help_text='Lieferant/Absender', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='vendor_address',
            field=models.TextField(blank=True, help_text='Lieferantenadresse', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='customer_name',
            field=models.CharField(blank=True, help_text='Kunde/Empfänger', max_length=255, null=True),
        ),
    ]
