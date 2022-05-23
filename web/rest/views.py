from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

import logging

from .serializers import JobSerializer, DocumentSerializer, OutputSerializer
from .models import Job, Document, Output
from .tasks import convert_doc


logger = logging.getLogger(__file__)


@csrf_exempt
def job_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = JobSerializer(data=data)
        logger.debug(serializer.initial_data)
        if serializer.is_valid():
            serializer.save()
            convert_doc.delay(serializer.data['id'])
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


def job_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = JobSerializer(job)
        return JsonResponse(serializer.data)

    # elif request.method == 'PUT':
    #     data = JSONParser().parse(request)
    #     serializer = SnippetSerializer(snippet, data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return JsonResponse(serializer.data)
    #     return JsonResponse(serializer.errors, status=400)
    #
    # elif request.method == 'DELETE':
    #     snippet.delete()
    #     return HttpResponse(status=204)
