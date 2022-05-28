from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('jobs/', views.ListJobs.as_view(), name='jobs'),
    path('jobs/<int:job_id>/', views.ViewJob.as_view(), name='job'),
    path('download/job_<int:job_id>/<str:filename>', views.DownloadOutput.as_view(), name='download'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
