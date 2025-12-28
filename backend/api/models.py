from typing import TYPE_CHECKING, Optional
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from .models import Role, Admin, Class

class User(AbstractUser):
    name: str = models.CharField(max_length=100)
    username: str = models.CharField(max_length=100, unique=True)
    password: str = models.CharField(max_length=100)

class Role(models.Model):
    name: str = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name

class Admin(models.Model):
    user: 'User' = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role: 'Role' = models.ForeignKey(Role, on_delete=models.CASCADE)
    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Class(models.Model):
    class_id: int = models.AutoField(primary_key=True)
    name: str = models.CharField(max_length=100)
    section: str = models.CharField(max_length=10)
    semester: str = models.CharField(max_length=10)
    year: int = models.IntegerField()
    admin: 'Admin' = models.ForeignKey(Admin, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} - {self.section}"

class Student(models.Model):
    user: 'User' = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name: str = models.CharField(max_length=50, blank=False, null=False)
    middle_name: Optional[str] = models.CharField(max_length=50, blank=True, null=True)
    last_name: str = models.CharField(max_length=50, blank=False, null=False)
    student_class: 'Class' = models.ForeignKey(Class, on_delete=models.CASCADE)
    student_img: models.ImageField = models.ImageField(upload_to='student_images')

    def __str__(self) -> str:
        return f"{self.first_name} {self.middle_name} {self.last_name}"

class Attendance(models.Model):
    PRESENT: str = 'Present'
    ABSENT: str = 'Absent'
    LATE: str = 'Late'
    STATUS_CHOICES: list[tuple[str, str]] = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (LATE, 'Late'),
    ]
    status: str = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)
    date_time: models.DateTime = models.DateTimeField(default=timezone.now)
    student: 'Student' = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.student} - {self.get_status_display()} on {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}"