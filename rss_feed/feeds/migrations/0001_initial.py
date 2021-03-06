# Generated by Django 3.0.9 on 2020-08-08 23:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.TextField()),
                ('xml_url', models.URLField()),
                ('link', models.URLField()),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('last_update', models.DateTimeField(blank=True, null=True)),
                ('is_followed', models.BooleanField(default=True)),
                ('is_auto_updated', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feeds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('created_by', 'xml_url')},
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.TextField()),
                ('link', models.URLField()),
                ('published_time', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('last_update', models.DateTimeField(blank=True, null=True)),
                ('state', models.CharField(choices=[('UNREAD', 'Unread'), ('READ', 'Read')], default='UNREAD', max_length=10)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='feeds.Feed')),
            ],
            options={
                'ordering': ('-published_time', '-last_update'),
            },
        ),
    ]
