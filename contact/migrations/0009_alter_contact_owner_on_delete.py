from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0008_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name=None, to=settings.AUTH_USER_MODEL, verbose_name='Proprietário'),
        ),
    ]
