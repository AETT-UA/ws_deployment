from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from rest.startup_scripts import create_users, create_course_units

schema_view = get_schema_view(
	openapi.Info(
		title="Attendance  REST API documentation",
		default_version='v2',
		description="Deti4devs REST API "
	),
	public=True,
	permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
	path('admin/', admin.site.urls),
	path("documentation/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
	path("", include("api.urls")),
]

if settings.DEBUG:
	create_users()
	create_course_units()
