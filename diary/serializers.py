from rest_framework import serializers
from .models import DiaryEntry, ContentBlock
import base64
from django.core.files.base import ContentFile


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

    def update(self, instance, validated_data):
        """Handle base64 file upload during update"""
        file_data = validated_data.pop('file_data', None)
        
        if file_data and file_data.startswith('data:'):
            # Parse base64 data URL
            format, datastr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # Create file from base64
            data = ContentFile(base64.b64decode(datastr))
            file_name = f"{validated_data.get('block_type', instance.block_type)}_{validated_data.get('order', instance.order)}.{ext}"
            
            # Delete old file if it exists
            if instance.media_file:
                instance.media_file.delete(save=False)
            
            # Save the new file
            instance.media_file.save(file_name, data, save=False)
        
        return super().update(instance, validated_data)
    
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
    
    class Meta:
        model = DiaryEntry
        fields = ('id', 'title', 'content_blocks', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        """Create diary entry with content blocks"""
        content_blocks_data = validated_data.pop('content_blocks', [])
        
        # Create the diary entry
        diary_entry = DiaryEntry.objects.create(**validated_data)
        
        # Create content blocks using the ContentBlockSerializer
        for block_data in content_blocks_data:
            block_serializer = ContentBlockSerializer(
                data=block_data,
                context=self.context
            )
            if block_serializer.is_valid(raise_exception=True):
                block_serializer.save(diary_entry=diary_entry)
        
        return diary_entry
    
    def update(self, instance, validated_data):
        """Update diary entry and optionally update content blocks"""
        content_blocks_data = validated_data.pop('content_blocks', None)
        
        # Update diary entry fields
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        
        # If content blocks are provided, update them intelligently
        if content_blocks_data is not None:
            existing_blocks = {block.id: block for block in instance.content_blocks.all()}
            kept_block_ids = set()
            
            for block_data in content_blocks_data:
                block_id = block_data.get('id')
                
                if block_id and block_id in existing_blocks:
                    # Update existing block
                    kept_block_ids.add(block_id)
                    block_instance = existing_blocks[block_id]
                    
                    block_serializer = ContentBlockSerializer(
                        block_instance,
                        data=block_data,
                        context=self.context,
                        partial=True
                    )
                    if block_serializer.is_valid(raise_exception=True):
                        block_serializer.save()
                else:
                    # Create new block
                    block_serializer = ContentBlockSerializer(
                        data=block_data,
                        context=self.context
                    )
                    if block_serializer.is_valid(raise_exception=True):
                        block_serializer.save(diary_entry=instance)
            
            # Delete blocks that are not in the new list
            for block_id, block in existing_blocks.items():
                if block_id not in kept_block_ids:
                    block.delete()
        
        return instance


class DiaryEntryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing diary entries"""
    
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    content_blocks_count = serializers.IntegerField(
        source='content_blocks.count',
        read_only=True
    )
    
    class Meta:
        model = DiaryEntry
        fields = (
            'id',
            'title',
            'author_email',
            'author_name',
            'content_blocks_count',
            'created_at',
            'updated_at'
        )
        read_only_fields = fields
