from rest_framework import serializers
from .models import Job, Document, Output, Status, Format

import logging

logger = logging.getLogger(__file__)


class BinaryDataField(serializers.Field):
    def to_representation(self, value):
        preview_length = 265
        s = str(value)
        if len(s) > preview_length:
            return f"{s[0:preview_length - 1]} [...]"
        return s

    def to_internal_value(self, data):
        return bytes(data, 'utf-8')


class DocumentSerializer(serializers.ModelSerializer):
    content = BinaryDataField(required=True)

    class Meta:
        model = Document
        fields = ['id', 'hash', 'content', 'time_created', 'time_updated']


class JobSerializer(serializers.ModelSerializer):
    document = DocumentSerializer()

    class Meta:
        model = Job
        fields = [
            'id',
            'document',
            'format',
            'time_created',
            'time_updated',
            'time_start',
            'time_end',
            'status',
            'message'
        ]

    def validate_document(self, value):
        logger.debug(f"Validating document {value}")
        return value

    def validate_format(self, value):
        formats = [fmt.value for fmt in Format]
        if value not in formats:
            raise serializers.ValidationError((
                f"Unsupported format requested ({value}). "
                f"Supported formats: {', '.join(formats)}."
            ))
        return value

    def create(self, validated_data):
        document = validated_data.pop('content')
        document_instance = DocumentSerializer.objects.get_or_create(content=document)
        instance = JobSerializer.objects.create(**validated_data, document=document_instance.id)
        return instance


class OutputSerializer(serializers.ModelSerializer):
    job = JobSerializer()

    class Meta:
        model = Output
        fields = [
            'id',
            'time_created',
            'time_updated',
            'job',
            'format',
            'file_path',
            'time_last_downloaded',
            'download_count'
        ]
