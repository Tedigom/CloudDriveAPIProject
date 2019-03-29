from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views,errorHandling

urlpatterns = format_suffix_patterns([
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('verification/',views.verification),
    path('errorHandling/',errorHandling.errorHandling),

])