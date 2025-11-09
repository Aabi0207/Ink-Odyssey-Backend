from django.urls import path
from .views import (
    DiaryEntryListCreateView,
    DiaryEntryDetailView,
    ContentBlockListCreateView,
    ContentBlockDetailView,
    DiaryEntryByDateView,
    DiaryStatsView,
)

urlpatterns = [
    # Diary entry endpoints
    path('entries/', DiaryEntryListCreateView.as_view(), name='diary-entry-list-create'),
    path('entries/<int:pk>/', DiaryEntryDetailView.as_view(), name='diary-entry-detail'),
    path('entries/by-date/', DiaryEntryByDateView.as_view(), name='diary-entry-by-date'),
    
    # Content block endpoints
    path('entries/<int:entry_id>/blocks/', ContentBlockListCreateView.as_view(), name='content-block-list-create'),
    path('entries/<int:entry_id>/blocks/<int:pk>/', ContentBlockDetailView.as_view(), name='content-block-detail'),
    
    # Statistics endpoint
    path('stats/', DiaryStatsView.as_view(), name='diary-stats'),
]
