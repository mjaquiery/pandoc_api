from rest_framework import serializers
from .models import Job, Status


class JobSerializer(serializers.Serializer):
    hash = serializers.CharField(read_only=True)
    document = serializers.CharField(required=True)

    time_created = serializers.DateTimeField(read_only=True)

    time_updated = serializers.DateTimeField(read_only=True)
    time_start = serializers.DateTimeField(read_only=True)
    time_end = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Job.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        if instance.status != Status.PENDING.value:
            raise PermissionError('Only documents pending processing can be changed.')

        instance.document = validated_data.get('document', instance.document)
        instance.save()
        return instance
