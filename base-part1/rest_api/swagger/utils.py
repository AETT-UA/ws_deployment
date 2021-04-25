from rest_framework import serializers


class ResponseSerializer(serializers.Serializer):
	token = serializers.CharField()
	success = serializers.ListField()
	errors = serializers.ListField()
	data = serializers.DictField()
