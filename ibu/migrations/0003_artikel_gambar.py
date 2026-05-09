from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ibu', '0002_add_artikel_edukasi'),
    ]

    operations = [
        migrations.AddField(
            model_name='artikeledukasi',
            name='gambar',
            field=models.ImageField(blank=True, null=True, upload_to='artikel/'),
        ),
    ]
