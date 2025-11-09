from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import DiaryEntry, ContentBlock
from .serializers import (
    DiaryEntrySerializer,
    DiaryEntryCreateSerializer,
    DiaryEntryListSerializer,
    ContentBlockSerializer
)


class DiaryEntryListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating diary entries.
    GET /api/diary/entries/ - List all diary entries for authenticated user
    POST /api/diary/entries/ - Create a new diary entry
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DiaryEntryCreateSerializer
        return DiaryEntrySerializer  # Changed to include content_blocks
    
    def get_queryset(self):
        """Return diary entries for the authenticated user only"""
        return DiaryEntry.objects.filter(
            author=self.request.user
        ).prefetch_related('content_blocks')
    
    def perform_create(self, serializer):
        """Set the author to the current user when creating"""
        serializer.save(author=self.request.user)


class DiaryEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a diary entry.
    GET /api/diary/entries/<id>/ - Retrieve a diary entry
    PUT/PATCH /api/diary/entries/<id>/ - Update a diary entry
    DELETE /api/diary/entries/<id>/ - Delete a diary entry
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DiaryEntryCreateSerializer
        return DiaryEntrySerializer
    
    def get_queryset(self):
        """Return diary entries for the authenticated user only"""
        return DiaryEntry.objects.filter(
            author=self.request.user
        ).prefetch_related('content_blocks')


class ContentBlockListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating content blocks for a specific diary entry.
    GET /api/diary/entries/<entry_id>/blocks/ - List all blocks
    POST /api/diary/entries/<entry_id>/blocks/ - Create a new block
    """
    serializer_class = ContentBlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return content blocks for a specific diary entry owned by the user"""
        entry_id = self.kwargs.get('entry_id')
        return ContentBlock.objects.filter(
            diary_entry_id=entry_id,
            diary_entry__author=self.request.user
        )
    
    def perform_create(self, serializer):
        """Create a content block for the specified diary entry"""
        entry_id = self.kwargs.get('entry_id')
        diary_entry = get_object_or_404(
            DiaryEntry,
            id=entry_id,
            author=self.request.user
        )
        serializer.save(diary_entry=diary_entry)


class ContentBlockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a content block.
    GET /api/diary/entries/<entry_id>/blocks/<id>/ - Retrieve a block
    PUT/PATCH /api/diary/entries/<entry_id>/blocks/<id>/ - Update a block
    DELETE /api/diary/entries/<entry_id>/blocks/<id>/ - Delete a block
    """
    serializer_class = ContentBlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return content blocks for a specific diary entry owned by the user"""
        entry_id = self.kwargs.get('entry_id')
        return ContentBlock.objects.filter(
            diary_entry_id=entry_id,
            diary_entry__author=self.request.user
        )


class DiaryEntryByDateView(APIView):
    """
    API endpoint for retrieving diary entries by date.
    GET /api/diary/entries/by-date/?date=YYYY-MM-DD
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'error': 'Date parameter is required (format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entries = DiaryEntry.objects.filter(
            author=request.user,
            created_at__date=date
        ).prefetch_related('content_blocks')
        
        serializer = DiaryEntrySerializer(entries, many=True)
        return Response(serializer.data)


class DiaryStatsView(APIView):
    """
    API endpoint for getting diary statistics.
    GET /api/diary/stats/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        user = request.user
        
        # Total entries
        total_entries = DiaryEntry.objects.filter(author=user).count()
        
        # Entries this month
        today = datetime.now()
        first_day_of_month = today.replace(day=1)
        entries_this_month = DiaryEntry.objects.filter(
            author=user,
            created_at__gte=first_day_of_month
        ).count()
        
        # Entries this week
        start_of_week = today - timedelta(days=today.weekday())
        entries_this_week = DiaryEntry.objects.filter(
            author=user,
            created_at__gte=start_of_week
        ).count()
        
        # Total content blocks
        total_blocks = ContentBlock.objects.filter(
            diary_entry__author=user
        ).count()
        
        # Block type distribution
        block_distribution = ContentBlock.objects.filter(
            diary_entry__author=user
        ).values('block_type').annotate(count=Count('id'))
        
        return Response({
            'total_entries': total_entries,
            'entries_this_month': entries_this_month,
            'entries_this_week': entries_this_week,
            'total_blocks': total_blocks,
            'block_distribution': list(block_distribution)
        })

