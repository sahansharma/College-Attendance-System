import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.files import File
from django.contrib.auth.hashers import make_password

from api.models import User, Admin, Class, Student, Attendance

# Image path (adjust this if needed)
STUDENT_IMAGE_PATH = r'C:\Users\sahan\one_dr_file\Documents\clg_prj\backend\student_images\temp_image.jpg'

# Nepali-style sample names (first, middle, last)
nepali_names = [
    ("Suman", "Prasad", "Shrestha"),
    ("Anita", "Kumar", "Thapa"),
    ("Binod", "Raj", "Gurung"),
    ("Pratik", "Man", "Rai"),
    ("Mina", "Laxmi", "Lama"),
    ("Sita", "Hari", "Magar"),
    ("Ramesh", "Kiran", "KC"),
    ("Pooja", "Manju", "Shahi"),
    ("Kiran", "Bikram", "Tamang"),
    ("Sarita", "Bala", "Basnet"),
]

def create_classes(admin):
    classes = []
    for sem in range(1, 3):  # two semesters
        for sec in ['A', 'B']:  # two sections
            class_name = f"CompSci{sem}0{sec}"
            c, _ = Class.objects.get_or_create(
                name=class_name,
                section=sec,
                semester=f"Semester {sem}",
                year=2025,
                admin=admin
            )
            classes.append(c)
    print(f"Created or found {len(classes)} classes for Admin id={admin.pk}")
    return classes

def create_students(classes):
    students_created = 0
    for cls in classes:
        count = random.randint(30, 50)
        for _ in range(count):
            first, middle, last = random.choice(nepali_names)
            username = (first + last).lower() + '123'
            password = f"{first[0].upper()}{last.lower()}123.@"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'name': f"{first} {middle} {last}",
                    'password': make_password(password)
                }
            )
            if created:
                with open(STUDENT_IMAGE_PATH, 'rb') as img_file:
                    django_file = File(img_file)
                    student = Student(
                        user=user,
                        first_name=first,
                        middle_name=middle,
                        last_name=last,
                        student_class=cls,
                    )
                    student.student_img.save(f"{username}.jpg", django_file, save=True)
                students_created += 1
    print(f"Created {students_created} new students.")

def generate_attendance(months_back=3):
    status_choices = ['Present', 'Absent', 'Late']
    status_weights = [0.8, 0.15, 0.05]
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=months_back * 30)
    students = Student.objects.all()

    def daterange(start_date, end_date):
        for n in range((end_date - start_date).days + 1):
            day = start_date + timedelta(n)
            # Only weekdays
            if day.weekday() < 5:
                yield day

    total_records = 0
    for student in students:
        for single_date in daterange(start_date, end_date):
            exists = Attendance.objects.filter(student=student, date_time__date=single_date).exists()
            if exists:
                continue
            hour = random.randint(8, 15)
            minute = random.randint(0, 59)
            attendance_datetime = datetime.combine(single_date, datetime.min.time()).replace(hour=hour, minute=minute)
            status = random.choices(status_choices, weights=status_weights, k=1)[0]
            Attendance.objects.create(
                student=student,
                status=status,
                date_time=attendance_datetime
            )
            total_records += 1
    print(f"Created {total_records} attendance records for {students.count()} students.")

def run_all():
    try:
        admin = Admin.objects.get(pk=6)
    except Admin.DoesNotExist:
        print("Admin with pk=6 does not exist. Please check.")
        return

    classes = create_classes(admin)
    create_students(classes)
    generate_attendance()

# Run this in Django shell or a script
if __name__ == '__main__':
    run_all()
