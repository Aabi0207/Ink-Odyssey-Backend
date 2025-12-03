from django.core.management.base import BaseCommand
from self_reflection.models import ReflectionQuestion


class Command(BaseCommand):
    help = 'Update color mappings for all existing reflection questions'

    def handle(self, *args, **options):
        questions = ReflectionQuestion.objects.all()
        updated_count = 0
        
        for question in questions:
            if not question.color_mapping:
                question.color_mapping = question.generate_color_mapping()
                question.save(update_fields=['color_mapping'])
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated colors for question: {question.question_text[:50]}...'
                    )
                )
        
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully updated {updated_count} question(s) with color mappings!'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No questions needed color mapping updates.'
                )
            )
