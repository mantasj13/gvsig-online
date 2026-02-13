# Modified to skip during initial migration
from django.db import migrations

def noop(apps, schema_editor):
    pass
        
class Migration(migrations.Migration):
    dependencies = [
        ('gvsigol_services', '0051_layer_vector_tile'),
    ]

    operations = [
        migrations.RunPython(noop, reverse_code=noop),
    ]
