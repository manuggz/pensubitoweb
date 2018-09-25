# Generated by Django 2.1.1 on 2018-09-24 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_misvoti', '0003_auto_20180924_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relacionmateriapensumbase',
            name='pensum',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api_misvoti.Pensum'),
        ),
        migrations.AlterField(
            model_name='relacionmateriapensumbase',
            name='tipo_materia',
            field=models.CharField(choices=[('RG', 'Regular'), ('GE', 'General'), ('EL', 'Electiva libre'), ('EA', 'Electiva de Area'), ('EX', 'Extraplan')], max_length=2),
        ),
    ]
