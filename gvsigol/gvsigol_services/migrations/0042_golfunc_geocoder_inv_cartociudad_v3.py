# Modified to skip during initial migration
from django.db import migrations

def noop(apps, schema_editor):
    pass
        
class Migration(migrations.Migration):
    dependencies = [
        ('gvsigol_services', '0041_golfunc_geocoder_inv_cartociudad_v2'),
    ]

    operations = [
        migrations.RunPython(noop, reverse_code=noop),
    ]
