import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.files import File
from django.contrib.auth.hashers import make_password

from api.models import User, Admin, Class, Student, Attendance
from admin_app.models import AdminUser

# Image path (adjust this if needed)
STUDENT_IMAGE_PATH = '/home/kali/Documents/Github/College-Attendance-System/backend/temp_image.jpg'

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
                try:
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
                except Exception as e:
                    print(f"Error creating student image for {username}: {e}")
    print(f"Created {students_created} new students.", flush=True)

def generate_attendance(months_back=1): # Reduced to 1 month for speed
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

    attendance_list = []
    for student in students:
        for single_date in daterange(start_date, end_date):
            exists = Attendance.objects.filter(student=student, date_time__date=single_date).exists()
            if exists:
                continue
            hour = random.randint(8, 15)
            minute = random.randint(0, 59)
            attendance_datetime = datetime.combine(single_date, datetime.min.time()).replace(hour=hour, minute=minute)
            # Make it aware if settings specify it
            attendance_datetime = timezone.make_aware(attendance_datetime)
            
            status = random.choices(status_choices, weights=status_weights, k=1)[0]
            attendance_list.append(Attendance(
                student=student,
                status=status,
                date_time=attendance_datetime
            ))
    
    if attendance_list:
        Attendance.objects.bulk_create(attendance_list)
    print(f"Created {len(attendance_list)} attendance records for {students.count()} students.", flush=True)

def run_all():
    from api.models import Role
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'name': 'Default Admin',
            'password': make_password('admin123'),
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    admin, _ = Admin.objects.get_or_create(
        user=admin_user,
        defaults={
            'role': admin_role,
            'first_name': 'Default',
            'last_name': 'Admin'
        }
    )

    # Also create for admin_app
    admin_app_user, created = AdminUser.objects.get_or_create(
        username='admin',
        defaults={
            'name': 'Default Admin',
            'password': make_password('admin123'),
            'is_staff': True,
            'is_superuser': True
        }
    )
    if not created:
        admin_app_user.password = make_password('admin123')
        admin_app_user.save()
    
    classes = create_classes(admin)
    create_students(classes)
    generate_attendance()

# Run this in Django shell or a script
if __name__ == '__main__':
    run_all()
