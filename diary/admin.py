from django.contrib import admin
from .models import DiaryEntry, ContentBlock


class ContentBlockInline(admin.TabularInline):
    """Inline admin for content blocks within diary entries"""
    model = ContentBlock
    extra = 1
    fields = ('block_type', 'order', 'text_content', 'media_file', 'media_url', 'caption')


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    """Admin configuration for DiaryEntry model"""
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'author__email', 'author__first_name', 'author__last_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ContentBlockInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author')


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    """Admin configuration for ContentBlock model"""
    list_display = ('id', 'diary_entry', 'block_type', 'order', 'created_at')
    list_filter = ('block_type', 'created_at')
    search_fields = ('diary_entry__title', 'text_content')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('diary_entry', 'diary_entry__author')

