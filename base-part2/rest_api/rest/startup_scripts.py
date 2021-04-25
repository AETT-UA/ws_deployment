from django.contrib.auth.models import User
from django.db import connection, IntegrityError

from api.models import CourseUnit, Department
from logs import exceptions_log

import xlrd

teachers = [
    {
        'email': 'professor1@ua.pt',
        'password': 'professor1',
        'first_name': 'professor1',
        'last_name': 'DETI'
    },
    {
        'email': 'professor2@ua.pt',
        'password': 'professor2',
        'first_name': 'professor2',
        'last_name': 'DETI'
    }
]

courses = [
    "PI",
    "MAS",
    "ITW",
    "TPW"
]


def create_users():
    table_name = User.objects.model._meta.db_table
    if table_name not in connection.introspection.table_names():
        return
    if User.objects.all().exists():
        return

    for user_data in teachers:
        password = user_data.pop('password')
        user_data['username'] = user_data['email']
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()


def create_course_units():
    table_name = CourseUnit.objects.model._meta.db_table
    if table_name not in connection.introspection.table_names():
        return
    if CourseUnit.objects.all().exists():
        return

    department = Department.objects.create(id=4, name="Departamento de Eletrónica, Telecomunicações e Informática",
                                           initials="DETI")
    for index, course in enumerate(courses):
        CourseUnit.objects.create(id=index, name=course, department=department)


def update_courses():

    def open_file(file_path):
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)

        for rowx in range(sheet.nrows)[1:]:
            yield sheet.row_values(rowx)[:-1]

    table_name = CourseUnit.objects.model._meta.db_table
    if table_name not in connection.introspection.table_names():
        return

    all_courses = list(CourseUnit.objects.all())

    for _id, name in open_file('Lista_Ucs.xlsx'):
        try:
            course = CourseUnit.objects.update_or_create(id=_id, defaults={"name": name})[0]
            if course in all_courses:
                all_courses.remove(course)
        except IntegrityError as error:
            exceptions_log.error(f"{__name__}->{update_courses.__name__} {error}")
            continue

    # Remaining courses -> to remove
    # for course in all_courses:
    #     course.delete()
