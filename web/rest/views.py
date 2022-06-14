import django.utils.timezone
from django.views.generic import View
from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.parsers import JSONParser
from rest_framework.serializers import ValidationError

import rest_framework.views
import logging
import os
import mimetypes

from .serializers import JobSerializer, OutputSerializer
from .models import Job, Document, Output, Format, Status
from .tasks import convert_doc


logger = logging.getLogger(__file__)


class ListJobs(rest_framework.views.APIView):
    """
    Jobs link a document to an output. They will take some time to complete.
    """
    def get(self, request: HttpRequest, **kwargs) -> Response:
        """
        View all jobs submitted to the system.
        TODO: paginate
        """
        output = []
        jobs = Job.objects.all()
        for job in jobs:
            data = {
                **JobSerializer(job).data,
                'output': OutputSerializer(Output.objects.filter(job_id=job.id), many=True).data
            }
            for o in data['output']:
                o.pop('job')
            output.append(data)

        return Response(output)

    @csrf_exempt
    def post(self, request: HttpRequest, **kwargs) -> Response:
        """
        Submit a job to the system.
        """
        # Check authorisation
        try:
            prefix, key = request.headers['Authorization'].split(' ')
            if prefix.lower() != 'bearer' or not key or key not in settings.AUTH_KEYS:
                return Response(status=401)
        except BaseException as e:
            logger.error(e)
            return Response(status=401)

        data = JSONParser().parse(request)

        # Create document
        content = data['content']
        document, doc_created = Document.objects.get_or_create(content=bytes(content, 'utf-8'))
        if doc_created:
            logger.debug(f"Created {document}.")
        else:
            logger.debug(f"Using existing {document}.")

        # Create job
        output_format = data['format']
        formats = [fmt.value for fmt in Format]
        if output_format not in formats:
            raise ValidationError((
                f"Unsupported format requested ({output_format}). "
                f"Supported formats: {', '.join(formats)}."
            ))

        job, job_created = Job.objects.get_or_create(
            document_id=document.id,
            format=output_format,
            auth_key=key
        )
        if job_created or job.status == Status.ERRORED.value:
            logger.debug(f"Created {job}." if job_created else f"Retrying errored {job}.")
            convert_doc.delay(job.id)
        else:
            logger.debug(f"Returning existing {job}.")
        serializer = JobSerializer(job)
        return Response(serializer.data, status=201)


class ViewJob(rest_framework.views.APIView):
    def get(self, request: HttpRequest, job_id, **kwargs) -> Response:
        """
        View the full details for a single job.
        """
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(status=404)

        serializer = JobSerializer(job)
        return Response({
            **serializer.data,
            'output': OutputSerializer(Output.objects.filter(job=job), many=True).data
        })


class DownloadOutput(View):
    def get(self, request: HttpRequest, job_id, filename, **kwargs) -> HttpResponse:
        """
        Expose a file for downloading and record the download.
        """
        path = os.path.join("/outputs", f"job_{job_id}", filename)
        output = Output.objects.get(file_path=path)
        output.time_last_downloaded = django.utils.timezone.now()
        output.download_count = output.download_count + 1
        output.save()

        file = open(path, 'rb')
        mime_type, _ = mimetypes.guess_type(path)
        response = HttpResponse(file, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = f"attachment; filename={os.path.basename(path)}"
        return response


class ListFormats(rest_framework.views.APIView):
    def get(self, request: HttpRequest, **kwargs) -> Response:
        """
        List the supported formats in which documents can be requested.
        """
        return Response([f.value for f in Format])
