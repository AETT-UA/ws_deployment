from django.urls import path, re_path

from api.views.department import all_departments, course_units_by_department
from api.views.accounts import login, register, profile, edit_profile, edit_password, logout
from api.views.attendance import course_units, create_attendance_sheet, attendance_status, students_in_attendance_sheet, \
    attendance_sheet_student_registration, attendance_sheet_student_deletion, attendance_sheets, attendance_info, course_units_my

urlpatterns = [
    # Accounts
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('profile', profile, name='profile'),
    path('profile/edit', edit_profile, name='edit_profile'),
    path('profile/password', edit_password, name='edit_password'),
    path('logout', logout, name='logout'),

    # Attendances
    path('course_units', course_units, name='course_units'),
    path('course_units/my', course_units_my, name='course_units_my'),
    path('attendance/sheet/new', create_attendance_sheet, name='create_attendance_sheet'),
    re_path(r'^attendance/sheet/(?P<sheet_id>\w+)$', attendance_info, name='attendance_info'),
    re_path('^attendance/sheets/(?P<course_id>[0-9]+)$', attendance_sheets, name='attendance_sheets'),
    re_path(r'^attendance/sheet/(?P<sheet_id>\w+)/status$', attendance_status, name='attendance_status'),
    re_path(r'^attendance/sheet/(?P<sheet_id>\w+)/students$', students_in_attendance_sheet,
            name='students_in_attendance_sheet'),
    re_path(r'^attendance/sheet/(?P<sheet_id>\w+)/student/registration$', attendance_sheet_student_registration,
            name='attendance_sheet_student_registration'),
    re_path(r'^attendance/sheet/(?P<sheet_id>\w+)/student/deletion$', attendance_sheet_student_deletion,
            name='attendance_sheet_student_deletion'),

    # Department
    path('department/all', all_departments, name='all_departments'),
    re_path('department/(?P<department_id>[0-9]+)/course_units', course_units_by_department,
            name='course_units_by_department'),
]
