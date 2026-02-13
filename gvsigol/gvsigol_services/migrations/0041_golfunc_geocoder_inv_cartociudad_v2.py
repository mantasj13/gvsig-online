# Modified to skip during initial migration
from django.db import migrations

def noop(apps, schema_editor):
    pass
        
class Migration(migrations.Migration):
    dependencies = [
        ('gvsigol_services', '0040_auto_20201022_1057'),
    ]

    operations = [
        migrations.RunPython(noop, reverse_code=noop),
    ]
