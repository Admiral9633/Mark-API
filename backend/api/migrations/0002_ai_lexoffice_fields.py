# Generated migration for AI classification and Lexoffice fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='ai_classification',
            field=models.JSONField(blank=True, help_text='Ollama AI classification result', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='is_invoice',
            field=models.BooleanField(default=False, help_text='AI detected this as an invoice'),
        ),
        migrations.AddField(
            model_name='document',
            name='invoice_type',
            field=models.CharField(blank=True, choices=[('incoming', 'Eingangsrechnung (zu bezahlen)'), ('outgoing', 'Ausgangsrechnung (von mir)')], help_text='Type of invoice: incoming or outgoing', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='lexoffice_sent',
            field=models.BooleanField(default=False, help_text='Uploaded to Lexoffice'),
        ),
        migrations.AddField(
            model_name='document',
            name='lexoffice_file_id',
            field=models.CharField(blank=True, help_text='Lexoffice file ID', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='lexoffice_voucher_id',
            field=models.CharField(blank=True, help_text='Lexoffice voucher ID', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='lexoffice_error',
            field=models.TextField(blank=True, help_text='Lexoffice upload error message', null=True),
        ),
    ]
