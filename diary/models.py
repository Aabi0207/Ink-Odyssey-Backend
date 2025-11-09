from django.db import models
from django.conf import settings
from django.utils import timezone


class DiaryEntry(models.Model):
    """
    Represents a diary entry.
    Each entry has a title and is associated with a user (author).
    Multiple entries can be created per day.
    """
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diary_entries'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Diary Entry'
        verbose_name_plural = 'Diary Entries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.author.email} ({self.created_at.date()})"


class ContentBlock(models.Model):
    """
    Represents a content block within a diary entry.
    Can be text, image, or video.
    """
    BLOCK_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )
    
    diary_entry = models.ForeignKey(
        DiaryEntry,
        on_delete=models.CASCADE,
        related_name='content_blocks'
    )
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)
    order = models.PositiveIntegerField(default=0)
    
    # Text content
    text_content = models.TextField(blank=True, null=True)
    
    # Media content (for images and videos)
    media_file = models.FileField(
        upload_to='diary_media/%Y/%m/%d/',
        blank=True,
        null=True
    )
    media_url = models.TextField(blank=True, null=True)  # For external URLs or base64 data
    caption = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Content Block'
        verbose_name_plural = 'Content Blocks'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['diary_entry', 'order']),
        ]
    
    def __str__(self):
        return f"{self.block_type.capitalize()} Block - {self.diary_entry.title}"
    
    def clean(self):
        """Validate that the content matches the block type"""
        from django.core.exceptions import ValidationError
        
        if self.block_type == 'text' and not self.text_content:
            raise ValidationError('Text blocks must have text content.')
        elif self.block_type in ['image', 'video'] and not (self.media_file or self.media_url):
            raise ValidationError(f'{self.block_type.capitalize()} blocks must have a media file or URL.')
    
    def delete(self, *args, **kwargs):
        """Delete the media file when deleting the content block"""
        if self.media_file:
            self.media_file.delete(save=False)
        super().delete(*args, **kwargs)
