from django.urls import path
from .views import TagSummaryView, MemoryArchiveViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'memories', MemoryArchiveViewSet, basename='memory-archive-memories')

urlpatterns = [
    path('tags-summary/', TagSummaryView.as_view(), name='tags-summary'),
] + router.urls
