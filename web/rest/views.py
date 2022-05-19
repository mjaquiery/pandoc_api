from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializers import JobSerializer

from .models import Job
# from .tasks import wait_5


@csrf_exempt
def job_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        # wait_5.delay()
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = JobSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
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
