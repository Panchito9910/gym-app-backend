"""Legacy migration - was a SQL Server workaround, now a no-op for all engines.
Kept for migration history compatibility.
"""
from django.db import migrations


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('token_blacklist', '0007_auto_20171017_2214'),
    ]

    operations = [
        migrations.RunPython(noop, noop),
    ]
