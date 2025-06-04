from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Student, Attendance

class Command(BaseCommand):
    help = 'Mark students as absent if they did not verify attendance by the end of the college day'

    def handle(self, *args, **kwargs):
        current_time = timezone.localtime(timezone.now())
        college_end_time = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
        self.stdout.write(self.style.SUCCESS(f'Checking attendance for {current_time}'))
        if current_time >= college_end_time:
            students = Student.objects.all()
            for student in students:
                last_attendance = Attendance.objects.filter(student=student).order_by('-date_time').first()
                if not last_attendance or last_attendance.date_time.date() != current_time.date():
                    Attendance.objects.create(status=Attendance.ABSENT, student=student, date_time=current_time)
                    self.stdout.write(self.style.SUCCESS(f'Marked {student.user.username} as absent'))
                else:
                    self.stdout.write(self.style.WARNING(f'{student.user.username} has already verified attendance today'))
        else:
            self.stdout.write(self.style.WARNING('It is not yet the end of the college day'))