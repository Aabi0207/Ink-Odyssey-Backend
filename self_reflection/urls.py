from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReflectionQuestionViewSet, SelfReflectionViewSet

router = DefaultRouter()
router.register(r'questions', ReflectionQuestionViewSet, basename='reflection-question')
router.register(r'reflections', SelfReflectionViewSet, basename='self-reflection')

urlpatterns = [
    path('', include(router.urls)),
]
