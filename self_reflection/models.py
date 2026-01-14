from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

# Color palette for question options (20 colors)
COLOR_PALETTE = [
    '#3291B6', '#BB8ED0', '#E0A8A8', '#9CC6DB', '#FCF6D9',
    '#CF4B00', '#DDBA7D', '#452829', '#57595B', '#E8D1C5',
    '#778873', '#A1BC98', '#9BB4C0', '#A72703', '#471396',
    '#EB5B00', '#6B3F69', '#86B0BD', '#932F67', '#015551'
]

# Heatmap colors for range questions (light to dark shades)
HEATMAP_COLORS = {
    'low': '#FCF6D9',      # Very light - for low values
    'medium_low': '#E8D1C5',
    'medium': '#DDBA7D',
    'medium_high': '#CF4B00',
    'high': '#A72703'      # Dark - for high values
}


class ReflectionQuestion(models.Model):
    """
    Represents a self-reflection question that can be asked to users.
    Questions can be of different types: range, multiple choice, text, or number.
    """
    QUESTION_TYPES = (
        ('range', 'Range (1-10)'),
        ('choice', 'Multiple Choice'),
        ('text', 'Text Response'),
        ('number', 'Number Input'),
    )
    
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='range')
    
    # For range questions (1-10)
    min_value = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    max_value = models.IntegerField(default=10, validators=[MaxValueValidator(10)])
    
    # For multiple choice questions - stored as JSON string
    # Example: ["Happy", "Sad", "Neutral", "Excited"]
    choices = models.JSONField(blank=True, null=True, help_text="List of choices for multiple choice questions")
    
    # Color mapping for options - automatically assigned from COLOR_PALETTE
    # For choice questions: {"option1": "#3291B6", "option2": "#BB8ED0", ...}
    # For range questions: {"1": "#FCF6D9", "5": "#DDBA7D", "10": "#A72703", ...}
    color_mapping = models.JSONField(blank=True, null=True, help_text="Color mapping for options/values")
    
    # Metadata
    is_active = models.BooleanField(default=True, help_text="Whether this question is currently being used")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    category = models.CharField(max_length=100, blank=True, help_text="Category like 'Productivity', 'Wellness', etc.")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reflection Question'
        verbose_name_plural = 'Reflection Questions'
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return f"{self.question_text} ({self.get_question_type_display()})"
    
    def clean(self):
        """Validate that choices are provided for multiple choice questions"""
        from django.core.exceptions import ValidationError
        
        if self.question_type == 'choice' and not self.choices:
            raise ValidationError('Multiple choice questions must have choices.')
        
        if self.question_type == 'range':
            if self.min_value >= self.max_value:
                raise ValidationError('Min value must be less than max value.')
    
    def generate_color_mapping(self):
        """Auto-generate color mapping based on question type"""
        if self.question_type == 'choice' and self.choices:
            # Assign colors from palette to each choice
            mapping = {}
            for idx, choice in enumerate(self.choices):
                if idx < len(COLOR_PALETTE):
                    mapping[choice] = COLOR_PALETTE[idx]
                else:
                    # If more than 20 choices, cycle through colors
                    mapping[choice] = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
            return mapping
        
        elif self.question_type == 'range':
            # Generate gradient colors for range (heatmap-friendly)
            mapping = {}
            range_size = self.max_value - self.min_value
            
            for value in range(self.min_value, self.max_value + 1):
                # Calculate position in range (0.0 to 1.0)
                if range_size > 0:
                    position = (value - self.min_value) / range_size
                else:
                    position = 0.5
                
                # Map to heatmap colors based on position
                if position < 0.2:
                    mapping[str(value)] = HEATMAP_COLORS['low']
                elif position < 0.4:
                    mapping[str(value)] = HEATMAP_COLORS['medium_low']
                elif position < 0.6:
                    mapping[str(value)] = HEATMAP_COLORS['medium']
                elif position < 0.8:
                    mapping[str(value)] = HEATMAP_COLORS['medium_high']
                else:
                    mapping[str(value)] = HEATMAP_COLORS['high']
            
            return mapping
        
        return {}
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate color mapping if not provided or if choices changed"""
        # Always regenerate color mapping for choice and range questions
        # This ensures colors are updated when choices are modified
        if self.question_type in ['choice', 'range']:
            self.color_mapping = self.generate_color_mapping()
        elif not self.color_mapping:
            self.color_mapping = self.generate_color_mapping()
        super().save(*args, **kwargs)


class SelfReflection(models.Model):
    """
    Represents a user's daily self-reflection entry.
    One reflection per user per day.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='self_reflections'
    )
    date = models.DateField(default=timezone.now)
    
    # Optional notes field for additional thoughts
    notes = models.TextField(blank=True, help_text="Additional thoughts or notes for the day")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Self Reflection'
        verbose_name_plural = 'Self Reflections'
        ordering = ['-date']
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.date}"


class ReflectionResponse(models.Model):
    """
    Represents a user's response to a specific reflection question for a specific day.
    """
    daily_reflection = models.ForeignKey(
        SelfReflection,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        ReflectionQuestion,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # Flexible response fields - use based on question type
    range_response = models.IntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Response for range-type questions"
    )
    choice_response = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Response for multiple choice questions"
    )
    text_response = models.TextField(
        blank=True, 
        null=True,
        help_text="Response for text-type questions"
    )
    number_response = models.FloatField(
        blank=True,
        null=True,
        help_text="Response for number-type questions (integer or decimal)"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reflection Response'
        verbose_name_plural = 'Reflection Responses'
        unique_together = ['daily_reflection', 'question']
        indexes = [
            models.Index(fields=['daily_reflection', 'question']),
        ]
    
    def __str__(self):
        return f"{self.daily_reflection.user.email} - {self.question.question_text[:50]} - {self.daily_reflection.date}"
    
    def clean(self):
        """Validate that the response matches the question type"""
        from django.core.exceptions import ValidationError
        
        if self.question.question_type == 'range' and self.range_response is None:
            raise ValidationError('Range questions must have a range response.')
        
        if self.question.question_type == 'choice' and not self.choice_response:
            raise ValidationError('Multiple choice questions must have a choice response.')
        
        if self.question.question_type == 'text' and not self.text_response:
            raise ValidationError('Text questions must have a text response.')
        
        if self.question.question_type == 'number' and self.number_response is None:
            raise ValidationError('Number questions must have a number response.')
        
        # Validate choice is in the allowed choices
        if self.question.question_type == 'choice' and self.choice_response:
            if self.choice_response not in self.question.choices:
                raise ValidationError(f'Invalid choice. Must be one of: {", ".join(self.question.choices)}')
