# Generated by Django 2.0.9 on 2019-02-07 04:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('standardpages', '0002_add_header_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informationpagerelatedpage',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Page'),
        ),
    ]
