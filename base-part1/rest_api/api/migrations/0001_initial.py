# Generated by Django 3.1.1 on 2021-04-13 12:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('initials', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('nmec', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseUnit',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.department')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('internal_id', models.AutoField(primary_key=True, serialize=False)),
                ('id', models.CharField(editable=False, max_length=6, unique=True)),
                ('summary', models.TextField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('register_timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('course_unit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.courseunit')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('students', models.ManyToManyField(to='api.Student')),
            ],
        ),
    ]
