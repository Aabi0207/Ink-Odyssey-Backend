from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from diary.models import DiaryEntry
from diary.serializers import DiaryEntrySerializer
from datetime import datetime

class TagSummaryView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if not year or not month:
            now = datetime.now()
            year = now.year
            month = now.month
            
        year = int(year)
        month = int(month)
        
        # Get all entries for the user in that month
        entries = DiaryEntry.objects.filter(
            author=request.user,
            created_at__year=year,
            created_at__month=month
        ).prefetch_related('tags')
        
        # We need counts for tags in this month
        tag_counts = {}
        date_tags = {}
        
        # Color palette for tags
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F06292', '#AED581', '#7986CB', '#4DB6AC', '#FFD54F'
        ]
        tag_colors = {}
        color_idx = 0
        
        for entry in entries:
            date_str = entry.created_at.date().isoformat()
            if date_str not in date_tags:
                date_tags[date_str] = set()
                
            for tag in entry.tags.all():
                tag_name = tag.name
                # tag counts
                tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
                
                # date tags
                date_tags[date_str].add(tag_name)
                
                if tag_name not in tag_colors:
                    tag_colors[tag_name] = colors[color_idx % len(colors)]
                    color_idx += 1
                    
        # format date tags
        formatted_date_tags = {
            date: [{"name": tag, "color": tag_colors[tag]} for tag in tags]
            for date, tags in date_tags.items()
        }
        
        formatted_tag_counts = [
            {"name": tag, "count": count, "color": tag_colors[tag]}
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return Response({
            "tag_counts": formatted_tag_counts,
            "date_tags": formatted_date_tags
        })

from rest_framework.pagination import PageNumberPagination

class MemoryArchivePagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 10

class MemoryArchiveViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DiaryEntrySerializer
    pagination_class = MemoryArchivePagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = DiaryEntry.objects.filter(author=user).prefetch_related('tags', 'content_blocks')
        
        tags = self.request.query_params.get('tag')
        date = self.request.query_params.get('date')
        order = self.request.query_params.get('order', '-created_at')
        
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            if tag_list:
                queryset = queryset.filter(tags__name__in=tag_list).distinct()
            
        if date:
            queryset = queryset.filter(created_at__date=date)
            
        if order in ['created_at', '-created_at']:
            queryset = queryset.order_by(order)
            
        return queryset
