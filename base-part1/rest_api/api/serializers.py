from rest_framework import serializers

from api.models import Attendance, CourseUnit, Department, Student


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def __init__(self, *args, **kwargs):
        self.ignore_fields = kwargs.pop('ignore_fields', [])
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        rep = super(UserSerializer, self).to_representation(instance)
        for field in self.ignore_fields:
            rep.pop(field, None)
        return rep


class CourseUnitSimpleSerializer(serializers.Serializer):
    course_unit = serializers.IntegerField()
    summary = serializers.CharField(required=False)


class AttendanceSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    course_unit_name = serializers.CharField()
    creator_name = serializers.CharField()
    is_active = serializers.BooleanField()


class AttendanceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('id', 'register_timestamp', 'summary')


class AttendanceStatusSerializer(serializers.Serializer):
    status = serializers.BooleanField()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class CourseUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseUnit
        fields = '__all__'


class StudentNmecSerializer(serializers.Serializer):
    nmecs = serializers.ListField(child=serializers.IntegerField())


class StudentSerializer(serializers.Serializer):
    nmec = serializers.IntegerField()
    name = serializers.CharField()
    timestamp = serializers.DateTimeField(required=False, read_only=True)


class PasswordEditSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()


def change_serializer_to_non_required(serializer):
    for field_name in serializer.fields:
        serializer.fields[field_name].required = False
    return serializer
