# Modified to skip during initial migration
from django.db import migrations

def noop(apps, schema_editor):
    pass
        
class Migration(migrations.Migration):
    dependencies = [
        ('gvsigol_services', '0056_layerreadwriteroles'),
    ]

    operations = [
        migrations.RunPython(noop, reverse_code=noop),
    ]
