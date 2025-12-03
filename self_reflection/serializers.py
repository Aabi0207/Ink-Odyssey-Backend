from rest_framework import serializers
from .models import ReflectionQuestion, SelfReflection, ReflectionResponse


class ReflectionQuestionSerializer(serializers.ModelSerializer):
    """Serializer for ReflectionQuestion model"""
    
    class Meta:
        model = ReflectionQuestion
        fields = [
            'id',
            'question_text',
            'question_type',
            'min_value',
            'max_value',
            'choices',
            'color_mapping',
            'is_active',
            'order',
            'category',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'color_mapping']
    
    def validate(self, data):
        """Custom validation"""
        question_type = data.get('question_type')
        
        # Validate multiple choice questions have choices
        if question_type == 'choice':
            choices = data.get('choices')
            if not choices or not isinstance(choices, list) or len(choices) < 2:
                raise serializers.ValidationError({
                    'choices': 'Multiple choice questions must have at least 2 choices as a list.'
                })
        
        # Validate range questions have valid min/max
        if question_type == 'range':
            min_val = data.get('min_value', 1)
            max_val = data.get('max_value', 10)
            if min_val >= max_val:
                raise serializers.ValidationError({
                    'min_value': 'Min value must be less than max value.'
                })
        
        return data


class ReflectionResponseSerializer(serializers.ModelSerializer):
    """Serializer for individual reflection responses"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    question_id = serializers.IntegerField(source='question.id', read_only=True)
    
    class Meta:
        model = ReflectionResponse
        fields = [
            'id',
            'question_id',
            'question_text',
            'question_type',
            'range_response',
            'choice_response',
            'text_response',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReflectionResponseCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating reflection responses"""
    question_id = serializers.IntegerField()
    range_response = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=10)
    choice_response = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    text_response = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    def validate(self, data):
        """Validate that at least one response field is provided"""
        question_id = data.get('question_id')
        
        try:
            question = ReflectionQuestion.objects.get(id=question_id, is_active=True)
        except ReflectionQuestion.DoesNotExist:
            raise serializers.ValidationError({'question_id': 'Invalid or inactive question.'})
        
        # Validate based on question type
        if question.question_type == 'range':
            if data.get('range_response') is None:
                raise serializers.ValidationError({'range_response': 'Range response is required for this question.'})
            # Validate range is within question's min/max
            if not (question.min_value <= data['range_response'] <= question.max_value):
                raise serializers.ValidationError({
                    'range_response': f'Response must be between {question.min_value} and {question.max_value}.'
                })
        
        elif question.question_type == 'choice':
            if not data.get('choice_response'):
                raise serializers.ValidationError({'choice_response': 'Choice response is required for this question.'})
            # Validate choice is in allowed choices
            if data['choice_response'] not in question.choices:
                raise serializers.ValidationError({
                    'choice_response': f'Invalid choice. Must be one of: {", ".join(question.choices)}'
                })
        
        elif question.question_type == 'text':
            if not data.get('text_response'):
                raise serializers.ValidationError({'text_response': 'Text response is required for this question.'})
        
        data['question'] = question
        return data


class SelfReflectionSerializer(serializers.ModelSerializer):
    """Serializer for SelfReflection with nested responses"""
    responses = ReflectionResponseSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = SelfReflection
        fields = [
            'id',
            'user_email',
            'date',
            'notes',
            'responses',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'created_at', 'updated_at']


class SelfReflectionCreateUpdateSerializer(serializers.Serializer):
    """Serializer for creating/updating self reflections with responses"""
    date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True)
    responses = ReflectionResponseCreateSerializer(many=True)
    
    def validate_responses(self, value):
        """Ensure no duplicate question responses"""
        question_ids = [r['question_id'] for r in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError('Cannot have multiple responses for the same question.')
        return value
    
    def create(self, validated_data):
        """Create a new daily reflection with responses"""
        responses_data = validated_data.pop('responses')
        user = self.context['request'].user
        date = validated_data.get('date')
        notes = validated_data.get('notes', '')
        
        # Get or create the self reflection
        daily_reflection, created = SelfReflection.objects.get_or_create(
            user=user,
            date=date,
            defaults={'notes': notes}
        )
        
        if not created:
            daily_reflection.notes = notes
            daily_reflection.save()
        
        # Create or update responses
        for response_data in responses_data:
            question = response_data.pop('question')
            
            # Remove None values to avoid overwriting existing data unnecessarily
            clean_data = {k: v for k, v in response_data.items() if v is not None and k != 'question_id'}
            
            ReflectionResponse.objects.update_or_create(
                daily_reflection=daily_reflection,
                question=question,
                defaults=clean_data
            )
        
        return daily_reflection
    
    def update(self, instance, validated_data):
        """Update an existing daily reflection"""
        responses_data = validated_data.pop('responses')
        
        # Update notes
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        
        # Update or create responses
        for response_data in responses_data:
            question = response_data.pop('question')
            
            # Remove None values
            clean_data = {k: v for k, v in response_data.items() if v is not None and k != 'question_id'}
            
            ReflectionResponse.objects.update_or_create(
                daily_reflection=instance,
                question=question,
                defaults=clean_data
            )
        
        return instance
