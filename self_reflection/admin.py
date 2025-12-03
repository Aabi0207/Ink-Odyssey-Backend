from django.contrib import admin
from .models import ReflectionQuestion, SelfReflection, ReflectionResponse


@admin.register(ReflectionQuestion)
class ReflectionQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'category', 'is_active', 'order', 'created_at']
    list_filter = ['question_type', 'is_active', 'category']
    search_fields = ['question_text', 'category']
    ordering = ['order', 'id']
    list_editable = ['is_active', 'order']


class ReflectionResponseInline(admin.TabularInline):
    model = ReflectionResponse
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    
    def get_fields(self, request, obj=None):
        fields = ['question', 'range_response', 'choice_response', 'text_response']
        if obj:
            fields.extend(['created_at', 'updated_at'])
        return fields


@admin.register(SelfReflection)
class SelfReflectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'created_at', 'updated_at']
    list_filter = ['date', 'created_at']
    search_fields = ['user__email', 'notes']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ReflectionResponseInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ReflectionResponse)
class ReflectionResponseAdmin(admin.ModelAdmin):
    list_display = ['daily_reflection', 'question', 'get_response_value', 'created_at']
    list_filter = ['question__question_type', 'created_at']
    search_fields = ['daily_reflection__user__email', 'question__question_text']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_response_value(self, obj):
        """Display the appropriate response based on question type"""
        if obj.question.question_type == 'range':
            return f"{obj.range_response}/{obj.question.max_value}"
        elif obj.question.question_type == 'choice':
            return obj.choice_response
        elif obj.question.question_type == 'text':
            return obj.text_response[:50] + '...' if len(obj.text_response or '') > 50 else obj.text_response
        return 'N/A'
    
    get_response_value.short_description = 'Response'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'daily_reflection', 
            'daily_reflection__user', 
            'question'
        )
