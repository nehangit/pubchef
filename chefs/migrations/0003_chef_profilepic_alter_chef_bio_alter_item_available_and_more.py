# Generated by Django 5.0 on 2024-01-08 05:36

import chefs.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chefs', '0002_chef_working'),
    ]

    operations = [
        migrations.AddField(
            model_name='chef',
            name='profilepic',
            field=models.ImageField(default='profilepics/default.jpg', upload_to=chefs.models.profilepic_image_path),
        ),
        migrations.AlterField(
            model_name='chef',
            name='bio',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='available',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=chefs.models.item_image_path)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chefs.item')),
            ],
        ),
    ]
