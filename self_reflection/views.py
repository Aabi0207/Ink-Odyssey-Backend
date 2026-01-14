from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, Min, Max
from collections import defaultdict
from .models import ReflectionQuestion, SelfReflection, ReflectionResponse
from .serializers import (
    ReflectionQuestionSerializer,
    SelfReflectionSerializer,
    SelfReflectionCreateUpdateSerializer,
    ReflectionResponseSerializer
)


class ReflectionQuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reflection questions.
    
    List: GET /api/self-reflection/questions/
    Create: POST /api/self-reflection/questions/
    Retrieve: GET /api/self-reflection/questions/{id}/
    Update: PUT/PATCH /api/self-reflection/questions/{id}/
    Delete: DELETE /api/self-reflection/questions/{id}/
    Active Questions: GET /api/self-reflection/questions/active/
    """
    queryset = ReflectionQuestion.objects.all()
    serializer_class = ReflectionQuestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Optionally filter by active status"""
        queryset = ReflectionQuestion.objects.all()
        
        # Filter by active status if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__iexact=category)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active questions ordered by display order"""
        questions = ReflectionQuestion.objects.filter(is_active=True).order_by('order', 'id')
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get list of all question categories"""
        categories = ReflectionQuestion.objects.filter(
            is_active=True
        ).values_list('category', flat=True).distinct()
        return Response({'categories': [c for c in categories if c]})


class SelfReflectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing self reflections.
    
    List: GET /api/self-reflection/reflections/
    Create: POST /api/self-reflection/reflections/
    Retrieve: GET /api/self-reflection/reflections/{id}/
    Update: PUT/PATCH /api/self-reflection/reflections/{id}/
    Delete: DELETE /api/self-reflection/reflections/{id}/
    Today: GET /api/self-reflection/reflections/today/
    By Date: GET /api/self-reflection/reflections/by_date/?date=YYYY-MM-DD
    Stats: GET /api/self-reflection/reflections/stats/
    """
    serializer_class = SelfReflectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get reflections for the current user"""
        return SelfReflection.objects.filter(
            user=self.request.user
        ).prefetch_related('responses', 'responses__question')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return SelfReflectionCreateUpdateSerializer
        return SelfReflectionSerializer
    
    def perform_create(self, serializer):
        """Save the reflection for the current user"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get or create today's reflection"""
        today = timezone.now().date()
        
        try:
            reflection = SelfReflection.objects.prefetch_related(
                'responses', 'responses__question'
            ).get(user=request.user, date=today)
            serializer = SelfReflectionSerializer(reflection)
            return Response(serializer.data)
        except SelfReflection.DoesNotExist:
            return Response(
                {
                    'detail': 'No reflection found for today.',
                    'date': today,
                    'has_reflection': False
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """Get reflection for a specific date"""
        date_str = request.query_params.get('date', None)
        
        if not date_str:
            return Response(
                {'detail': 'Date parameter is required (format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'detail': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reflection = SelfReflection.objects.prefetch_related(
                'responses', 'responses__question'
            ).get(user=request.user, date=date)
            serializer = SelfReflectionSerializer(reflection)
            return Response(serializer.data)
        except SelfReflection.DoesNotExist:
            return Response(
                {
                    'detail': f'No reflection found for {date}',
                    'date': date,
                    'has_reflection': False
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def date_range(self, request):
        """Get reflections for a date range"""
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        if not start_date or not end_date:
            return Response(
                {'detail': 'Both start_date and end_date are required (format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'detail': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reflections = self.get_queryset().filter(date__range=[start, end])
        serializer = SelfReflectionSerializer(reflections, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about user's reflections"""
        # Get date range (default to last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        reflections = self.get_queryset().filter(date__gte=start_date)
        
        total_reflections = reflections.count()
        
        # Get response statistics for range questions
        range_questions = ReflectionQuestion.objects.filter(question_type='range', is_active=True)
        question_stats = []
        
        for question in range_questions:
            responses = ReflectionResponse.objects.filter(
                daily_reflection__in=reflections,
                question=question,
                range_response__isnull=False
            )
            
            avg_value = responses.aggregate(avg=Avg('range_response'))['avg']
            
            if avg_value is not None:
                question_stats.append({
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'average': round(avg_value, 2),
                    'count': responses.count()
                })
        
        # Calculate streak
        current_streak = self._calculate_streak(request.user)
        
        return Response({
            'total_reflections': total_reflections,
            'days_analyzed': days,
            'current_streak': current_streak,
            'question_averages': question_stats
        })
    
    @action(detail=False, methods=['get'])
    def streak(self, request):
        """Get the user's current reflection streak"""
        streak = self._calculate_streak(request.user)
        return Response({'current_streak': streak})
    
    def _calculate_streak(self, user):
        """Calculate the current streak of consecutive days with reflections"""
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        while True:
            if SelfReflection.objects.filter(user=user, date=current_date).exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create or update multiple reflections at once"""
        if not isinstance(request.data, list):
            return Response(
                {'detail': 'Expected a list of reflections'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SelfReflectionCreateUpdateSerializer(
            data=request.data,
            many=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            reflections = []
            for item_data in serializer.validated_data:
                item_serializer = SelfReflectionCreateUpdateSerializer(
                    data=item_data,
                    context={'request': request}
                )
                if item_serializer.is_valid():
                    reflection = item_serializer.save()
                    reflections.append(reflection)
            
            output_serializer = SelfReflectionSerializer(reflections, many=True)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        Get comprehensive statistics for dashboard visualizations.
        Includes line charts data, heatmap data, and distribution data.
        
        Query params:
        - days: Number of days to analyze (default: 30)
        - question_id: Specific question to analyze (optional)
        """
        days = int(request.query_params.get('days', 30))
        question_id = request.query_params.get('question_id', None)
        start_date = timezone.now().date() - timedelta(days=days)
        
        reflections = self.get_queryset().filter(date__gte=start_date)
        
        # Get all active questions or specific question
        if question_id:
            questions = ReflectionQuestion.objects.filter(id=question_id, is_active=True)
        else:
            questions = ReflectionQuestion.objects.filter(is_active=True)
        
        dashboard_data = {
            'overview': {
                'total_reflections': reflections.count(),
                'days_analyzed': days,
                'current_streak': self._calculate_streak(request.user),
                'start_date': start_date.isoformat(),
                'end_date': timezone.now().date().isoformat()
            },
            'questions': []
        }
        
        for question in questions:
            question_data = {
                'question_id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'category': question.category,
                'color_mapping': question.color_mapping,
            }
            
            if question.question_type == 'range':
                # Get time series data for line chart
                question_data['line_chart'] = self._get_range_line_chart_data(
                    question, reflections, start_date, days
                )
                
                # Get heatmap data (calendar heatmap)
                question_data['heatmap'] = self._get_range_heatmap_data(
                    question, reflections, start_date, days
                )
                
                # Get distribution data
                question_data['distribution'] = self._get_range_distribution(
                    question, reflections
                )
                
            elif question.question_type == 'choice':
                # Get choice distribution over time for line chart
                question_data['line_chart'] = self._get_choice_line_chart_data(
                    question, reflections, start_date, days
                )
                
                # Get overall choice distribution
                question_data['distribution'] = self._get_choice_distribution(
                    question, reflections
                )
            
            elif question.question_type == 'number':
                # Get time series data for line chart (similar to range)
                question_data['line_chart'] = self._get_number_line_chart_data(
                    question, reflections, start_date, days
                )
            
            dashboard_data['questions'].append(question_data)
        
        return Response(dashboard_data)
    
    def _get_range_line_chart_data(self, question, reflections, start_date, days):
        """Generate line chart data for range questions"""
        responses = ReflectionResponse.objects.filter(
            daily_reflection__in=reflections,
            question=question,
            range_response__isnull=False
        ).select_related('daily_reflection')
        
        # Create date-indexed data
        data_points = []
        current_date = start_date
        end_date = timezone.now().date()
        
        # Group responses by date
        response_by_date = {}
        for response in responses:
            response_by_date[response.daily_reflection.date] = response.range_response
        
        while current_date <= end_date:
            value = response_by_date.get(current_date)
            data_points.append({
                'date': current_date.isoformat(),
                'value': value,
                'color': question.color_mapping.get(str(value)) if value and question.color_mapping else None
            })
            current_date += timedelta(days=1)
        
        # Calculate statistics
        values = [r.range_response for r in responses]
        stats = {
            'average': round(sum(values) / len(values), 2) if values else None,
            'min': min(values) if values else None,
            'max': max(values) if values else None,
            'count': len(values)
        }
        
        return {
            'data': data_points,
            'statistics': stats
        }
    
    def _get_range_heatmap_data(self, question, reflections, start_date, days):
        """Generate calendar heatmap data for range questions"""
        responses = ReflectionResponse.objects.filter(
            daily_reflection__in=reflections,
            question=question,
            range_response__isnull=False
        ).select_related('daily_reflection')
        
        heatmap_data = []
        for response in responses:
            value = response.range_response
            heatmap_data.append({
                'date': response.daily_reflection.date.isoformat(),
                'value': value,
                'color': question.color_mapping.get(str(value)) if question.color_mapping else None,
                'intensity': (value - question.min_value) / (question.max_value - question.min_value)
            })
        
        return heatmap_data
    
    def _get_range_distribution(self, question, reflections):
        """Get distribution of values for range questions"""
        responses = ReflectionResponse.objects.filter(
            daily_reflection__in=reflections,
            question=question,
            range_response__isnull=False
        )
        
        # Count occurrences of each value
        distribution = {}
        for value in range(question.min_value, question.max_value + 1):
            count = responses.filter(range_response=value).count()
            distribution[str(value)] = {
                'count': count,
                'percentage': 0,
                'color': question.color_mapping.get(str(value)) if question.color_mapping else None
            }
        
        # Calculate percentages
        total = responses.count()
        if total > 0:
            for value_str in distribution:
                distribution[value_str]['percentage'] = round(
                    (distribution[value_str]['count'] / total) * 100, 1
                )
        
        return distribution
    
    def _get_choice_line_chart_data(self, question, reflections, start_date, days):
        """Generate line chart data for choice questions (choice frequency over time)"""
        responses = ReflectionResponse.objects.filter(
            daily_reflection__in=reflections,
            question=question,
            choice_response__isnull=False
        ).select_related('daily_reflection')
        
        # Group by choice and date
        choice_data = defaultdict(list)
        current_date = start_date
        end_date = timezone.now().date()
        
        # Initialize all choices
        for choice in question.choices:
            choice_data[choice] = []
        
        # Collect responses
        response_by_date = {}
        for response in responses:
            response_by_date[response.daily_reflection.date] = response.choice_response
        
        # Create time series for each choice
        while current_date <= end_date:
            selected_choice = response_by_date.get(current_date)
            for choice in question.choices:
                choice_data[choice].append({
                    'date': current_date.isoformat(),
                    'selected': choice == selected_choice,
                    'value': 1 if choice == selected_choice else 0
                })
            current_date += timedelta(days=1)
        
        # Format for output
        datasets = []
        for choice in question.choices:
            datasets.append({
                'label': choice,
                'color': question.color_mapping.get(choice) if question.color_mapping else None,
                'data': choice_data[choice]
            })
        
        return {
            'datasets': datasets,
            'total_responses': responses.count()
        }
    
    def _get_choice_distribution(self, question, reflections):
        """Get distribution of choices for choice questions"""
        responses = ReflectionResponse.objects.filter(
            daily_reflection__in=reflections,
            question=question,
            choice_response__isnull=False
        )
        
        distribution = {}
        total = responses.count()
        
        for choice in question.choices:
            count = responses.filter(choice_response=choice).count()
            distribution[choice] = {
                'count': count,
                'percentage': round((count / total) * 100, 1) if total > 0 else 0,
                'color': question.color_mapping.get(choice) if question.color_mapping else None
            }
        
        return distribution

    def _get_number_line_chart_data(self, question, reflections, start_date, days):
        """Generate line chart data for number questions"""
        responses = ReflectionResponse.objects.filter(
            daily_reflection__in=reflections,
            question=question,
            number_response__isnull=False
        ).select_related('daily_reflection')
        
        # Create date-indexed data
        data_points = []
        current_date = start_date
        end_date = timezone.now().date()
        
        # Group responses by date
        response_by_date = {}
        for response in responses:
            response_by_date[response.daily_reflection.date] = response.number_response
        
        while current_date <= end_date:
            value = response_by_date.get(current_date)
            data_points.append({
                'date': current_date.isoformat(),
                'value': round(value, 2) if value is not None else None,
            })
            current_date += timedelta(days=1)
        
        # Calculate statistics
        values = [r.number_response for r in responses]
        stats = {
            'average': round(sum(values) / len(values), 2) if values else None,
            'min': round(min(values), 2) if values else None,
            'max': round(max(values), 2) if values else None,
            'count': len(values)
        }
        
        return {
            'data': data_points,
            'statistics': stats
        }
