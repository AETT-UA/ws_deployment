from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Department(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    initials = models.CharField(max_length=10)


class CourseUnit(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Student(models.Model):
    nmec = models.IntegerField(primary_key=True)
    name = models.TextField()
    timestamp = models.DateTimeField(default=now, editable=False, null=True)


class Attendance(models.Model):
    internal_id = models.AutoField(primary_key=True)
    id = models.CharField(unique=True, editable=False, max_length=6)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    course_unit = models.ForeignKey(CourseUnit, on_delete=models.PROTECT)
    summary = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    register_timestamp = models.DateTimeField(default=now, editable=False)

    students = models.ManyToManyField(Student)
