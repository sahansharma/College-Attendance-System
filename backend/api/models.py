from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Custom User model
class User(AbstractUser):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    
    REQUIRED_FIELDS = []


class Role(models.Model):
    
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Class(models.Model):
    class_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    year = models.IntegerField()
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.section}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    student_img = models.ImageField(upload_to='student_images')

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"


class Attendance(models.Model):
    PRESENT = 'Present'
    ABSENT = 'Absent'
    LATE = 'Late'
    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (LATE, 'Late'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)
    date_time = models.DateTimeField(default=timezone.now)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} - {self.get_status_display()} on {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}"
