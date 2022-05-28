from rest_framework import serializers
from .models import Job, Output

import logging

logger = logging.getLogger(__file__)


class JobSerializer(serializers.ModelSerializer):

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
