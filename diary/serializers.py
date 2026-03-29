from rest_framework import serializers
from .models import DiaryEntry, ContentBlock, DiaryTag
import base64
from django.core.files.base import ContentFile


class DiaryTagSerializer(serializers.ModelSerializer):
    """Serializer for DiaryTag model"""

    class Meta:
        model = DiaryTag
        fields = ('id', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')


class ContentBlockSerializer(serializers.ModelSerializer):
    """Serializer for ContentBlock model"""
    
    # Add a custom field to handle base64 file uploads
    file_data = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = ContentBlock
        fields = (
            'id',
            'block_type',
            'order',
            'text_content',
            'media_file',
            'media_url',
            'caption',
            'created_at',
            'file_data'
        )
        read_only_fields = ('id', 'created_at', 'media_file')
    
    def validate(self, data):
        """Validate that the content matches the block type"""
        block_type = data.get('block_type')
        text_content = data.get('text_content')
        media_url = data.get('media_url')
        file_data = data.get('file_data')
        
        if block_type == 'text' and not text_content:
            raise serializers.ValidationError(
                {'text_content': 'Text blocks must have text content.'}
            )
        elif block_type in ['image', 'video'] and not (file_data or media_url):
            raise serializers.ValidationError(
                {'file_data': f'{block_type.capitalize()} blocks must have a file or URL.'}
            )
        
        return data
    
    def create(self, validated_data):
        """Handle base64 file upload during creation"""
        file_data = validated_data.pop('file_data', None)
        
        if file_data and file_data.startswith('data:'):
            # Parse base64 data URL
            format, datastr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # Create file from base64
            data = ContentFile(base64.b64decode(datastr))
            file_name = f"{validated_data['block_type']}_{validated_data['order']}.{ext}"
            
            # Save the file
            content_block = ContentBlock(**validated_data)
            content_block.media_file.save(file_name, data, save=False)
            content_block.save()
            return content_block
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Customize the output to include the full media URL"""
        representation = super().to_representation(instance)
        
        # If media_file exists, provide the full URL
        if instance.media_file:
            request = self.context.get('request')
            if request:
                representation['media_url'] = request.build_absolute_uri(instance.media_file.url)
            else:
                representation['media_url'] = instance.media_file.url
        
        return representation


class DiaryEntrySerializer(serializers.ModelSerializer):
    """Serializer for DiaryEntry model with nested content blocks"""
    
    content_blocks = ContentBlockSerializer(many=True, read_only=True)
    tags = DiaryTagSerializer(many=True, read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = DiaryEntry
        fields = (
            'id',
            'title',
            'author',
            'author_email',
            'author_name',
            'content_blocks',
            'tags',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Pass context to nested serializers"""
        representation = super().to_representation(instance)
        
        # Re-serialize content_blocks with context to get proper URLs
        if instance.content_blocks.exists():
            content_blocks_serializer = ContentBlockSerializer(
                instance.content_blocks.all(),
                many=True,
                context=self.context
            )
            representation['content_blocks'] = content_blocks_serializer.data
        
        return representation


class DiaryEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating diary entries with content blocks"""
    
    content_blocks = ContentBlockSerializer(many=True, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        write_only=True
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True
    )
    tag_details = DiaryTagSerializer(source='tags', many=True, read_only=True)
    
    class Meta:
        model = DiaryEntry
        fields = (
            'id',
            'title',
            'content_blocks',
            'tag_ids',
            'tags',
            'tag_details',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def _get_or_create_tags(self, user, tag_names):
        normalized_names = [name.strip() for name in tag_names if name and name.strip()]
        unique_names = list(dict.fromkeys(normalized_names))
        result = []
        for name in unique_names:
            tag, _ = DiaryTag.objects.get_or_create(author=user, name=name)
            result.append(tag)
        return result

    def _get_tags_from_ids(self, user, tag_ids):
        tags = list(DiaryTag.objects.filter(author=user, id__in=tag_ids))
        if len(tags) != len(set(tag_ids)):
            raise serializers.ValidationError({'tag_ids': 'One or more tag IDs are invalid for this user.'})
        return tags
    
    def create(self, validated_data):
        """Create diary entry with content blocks"""
        content_blocks_data = validated_data.pop('content_blocks', [])
        tag_ids = validated_data.pop('tag_ids', [])
        tag_names = validated_data.pop('tags', [])
        
        # Create the diary entry
        diary_entry = DiaryEntry.objects.create(**validated_data)

        selected_tags = []
        if tag_ids:
            selected_tags.extend(self._get_tags_from_ids(diary_entry.author, tag_ids))
        if tag_names:
            selected_tags.extend(self._get_or_create_tags(diary_entry.author, tag_names))
        if selected_tags:
            diary_entry.tags.set(list({tag.id: tag for tag in selected_tags}.values()))
        
        # Create content blocks using the ContentBlockSerializer
        for block_data in content_blocks_data:
            block_serializer = ContentBlockSerializer(
                data=block_data,
                context=self.context
            )
            if block_serializer.is_valid():
                block_serializer.save(diary_entry=diary_entry)
        
        return diary_entry
    
    def update(self, instance, validated_data):
        """Update diary entry and optionally update content blocks"""
        content_blocks_data = validated_data.pop('content_blocks', None)
        tag_ids = validated_data.pop('tag_ids', None)
        tag_names = validated_data.pop('tags', None)
        
        # Update diary entry fields
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        
        # If content blocks are provided, delete old ones and create new ones
        if content_blocks_data is not None:
            # Delete old media files
            for block in instance.content_blocks.all():
                if block.media_file:
                    block.media_file.delete(save=False)
            instance.content_blocks.all().delete()
            
            # Create new content blocks
            for block_data in content_blocks_data:
                block_serializer = ContentBlockSerializer(
                    data=block_data,
                    context=self.context
                )
                if block_serializer.is_valid():
                    block_serializer.save(diary_entry=instance)

        if tag_ids is not None or tag_names is not None:
            selected_tags = []
            if tag_ids is not None:
                selected_tags.extend(self._get_tags_from_ids(instance.author, tag_ids))
            if tag_names is not None:
                selected_tags.extend(self._get_or_create_tags(instance.author, tag_names))
            unique_selected_tags = list({tag.id: tag for tag in selected_tags}.values())
            instance.tags.set(unique_selected_tags)
        
        return instance


class DiaryEntryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing diary entries"""
    
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    content_blocks_count = serializers.IntegerField(
        source='content_blocks.count',
        read_only=True
    )
    tags = DiaryTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = DiaryEntry
        fields = (
            'id',
            'title',
            'author_email',
            'author_name',
            'content_blocks_count',
            'tags',
            'created_at',
            'updated_at'
        )
        read_only_fields = fields
