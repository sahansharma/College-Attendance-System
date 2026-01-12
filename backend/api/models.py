from typing import TYPE_CHECKING, Optional
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime

if TYPE_CHECKING:
    from .models import Role, Admin, Class, Student


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    name: str = models.CharField(max_length=100)
    username: str = models.CharField(max_length=100, unique=True)
    password: str = models.CharField(max_length=100)


class Role(models.Model):
    """Role model for defining user roles."""
    name: str = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Admin(models.Model):
    """Admin model linking user with role and personal information."""
    user: 'User' = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role: 'Role' = models.ForeignKey(Role, on_delete=models.CASCADE)
    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Class(models.Model):
    """Class model representing academic classes."""
    class_id: int = models.AutoField(primary_key=True)
    name: str = models.CharField(max_length=100)
    section: str = models.CharField(max_length=10)
    semester: str = models.CharField(max_length=10)
    year: int = models.IntegerField()
    admin: 'Admin' = models.ForeignKey(Admin, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} - {self.section}"


class Student(models.Model):
    """Student model representing enrolled students."""
    user: 'User' = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name: str = models.CharField(max_length=50, blank=False, null=False)
    middle_name: Optional[str] = models.CharField(max_length=50, blank=True, null=True)
    last_name: str = models.CharField(max_length=50, blank=False, null=False)
    student_class: 'Class' = models.ForeignKey(Class, on_delete=models.CASCADE)
    student_img: models.ImageField = models.ImageField(upload_to='student_images')

    def __str__(self) -> str:
        return f"{self.first_name} {self.middle_name} {self.last_name}"


class Attendance(models.Model):
    """Attendance model tracking student attendance records."""
    PRESENT: str = 'Present'
    ABSENT: str = 'Absent'
    LATE: str = 'Late'
    STATUS_CHOICES: list[tuple[str, str]] = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (LATE, 'Late'),
    ]
    status: str = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)
    date_time: datetime.datetime = models.DateTimeField(default=timezone.now)
    student: 'Student' = models.ForeignKey(Student, on_delete=models.CASCADE)
    method: Optional['AttendanceMethod'] = models.ForeignKey(
        'AttendanceMethod', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='attendances'
    )
    
    def __str__(self) -> str:
        return f"{self.student} - {self.get_status_display()} on {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}"


class AttendanceMethod(models.Model):
    """
    Enum-like model for tracking available attendance methods.
    
    This model defines the different methods by which attendance can be recorded,
    such as PIN entry, QR code scanning, NFC card tapping, or fingerprint scanning.
    """
    PIN: str = 'PIN'
    QR: str = 'QR'
    NFC: str = 'NFC'
    FINGERPRINT: str = 'FINGERPRINT'
    FACE: str = 'FACE'
    
    METHOD_CHOICES: list[tuple[str, str]] = [
        (PIN, 'PIN Entry'),
        (QR, 'QR Code'),
        (NFC, 'NFC Card'),
        (FINGERPRINT, 'Fingerprint'),
        (FACE, 'Face Recognition'),
    ]
    
    name: str = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        unique=True,
        db_index=True
    )
    description: str = models.TextField(blank=True, null=True)
    is_active: bool = models.BooleanField(default=True)
    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime.datetime = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_attendancemethod'
        verbose_name = 'Attendance Method'
        verbose_name_plural = 'Attendance Methods'
    
    def __str__(self) -> str:
        return self.get_name_display()


class ClassAttendanceMethod(models.Model):
    """
    Links attendance methods to classes with configuration.
    
    This model allows configuring which attendance methods are available
    for a specific class, whether each method is required, and any
    method-specific configuration.
    """
    class_id: 'Class' = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE,
        related_name='attendance_methods'
    )
    method_id: 'AttendanceMethod' = models.ForeignKey(
        AttendanceMethod, 
        on_delete=models.CASCADE,
        related_name='class_methods'
    )
    is_required: bool = models.BooleanField(default=False)
    config: dict = models.JSONField(default=dict, blank=True)
    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime.datetime = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_classattendancemethod'
        verbose_name = 'Class Attendance Method'
        verbose_name_plural = 'Class Attendance Methods'
        unique_together = ['class_id', 'method_id']
        indexes = [
            models.Index(fields=['class_id', 'method_id'], name='class_method_idx'),
        ]
    
    def __str__(self) -> str:
        return f"{self.class_id} - {self.method_id}"


class StudentPIN(models.Model):
    """
    Secure PIN storage for students with rate limiting.
    
    This model stores the hashed PIN for each student and tracks
    failed attempts and lockout status for security.
    """
    student_id: 'Student' = models.OneToOneField(
        Student, 
        on_delete=models.CASCADE,
        related_name='pin'
    )
    pin_hash: str = models.CharField(max_length=255)
    failed_attempts: int = models.IntegerField(default=0)
    locked_until: Optional[datetime.datetime] = models.DateTimeField(null=True, blank=True)
    is_set: bool = models.BooleanField(default=False)
    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime.datetime = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_studentpin'
        verbose_name = 'Student PIN'
        verbose_name_plural = 'Student PINs'
        indexes = [
            models.Index(fields=['student_id'], name='student_pin_idx'),
            models.Index(fields=['locked_until'], name='pin_locked_idx'),
        ]
    
    def __str__(self) -> str:
        return f"PIN for {self.student_id}"
    
    def is_locked(self) -> bool:
        """Check if the PIN is currently locked."""
        if self.locked_until is None:
            return False
        return timezone.now() < self.locked_until


class ClassSession(models.Model):
    """
    Active attendance sessions for classes.
    
    This model manages active attendance sessions with unique session codes
    that can be used by students to mark their attendance.
    """
    class_id: 'Class' = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_code: str = models.CharField(max_length=10, unique=True, db_index=True)
    started_at: datetime.datetime = models.DateTimeField(default=timezone.now)
    expires_at: datetime.datetime = models.DateTimeField()
    is_active: bool = models.BooleanField(default=True)
    created_by: Optional['Admin'] = models.ForeignKey(
        Admin, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        db_table = 'api_classsession'
        verbose_name = 'Class Session'
        verbose_name_plural = 'Class Sessions'
        indexes = [
            models.Index(fields=['class_id', 'is_active'], name='session_class_active_idx'),
            models.Index(fields=['expires_at'], name='session_expires_idx'),
        ]
    
    def __str__(self) -> str:
        return f"Session {self.session_code} for {self.class_id}"
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return timezone.now() > self.expires_at


class NFCCard(models.Model):
    """
    NFC card mappings for students.
    
    This model stores the NFC card UID associated with each student,
    allowing attendance marking via NFC card tap.
    """
    student_id: 'Student' = models.OneToOneField(
        Student, 
        on_delete=models.CASCADE,
        related_name='nfc_card'
    )
    card_uid: str = models.CharField(max_length=64, unique=True, db_index=True)
    is_active: bool = models.BooleanField(default=True)
    issued_at: datetime.datetime = models.DateTimeField(default=timezone.now)
    expires_at: Optional[datetime.datetime] = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_nfccard'
        verbose_name = 'NFC Card'
        verbose_name_plural = 'NFC Cards'
        indexes = [
            models.Index(fields=['card_uid'], name='nfc_card_uid_idx'),
            models.Index(fields=['student_id'], name='nfc_student_idx'),
        ]
    
    def __str__(self) -> str:
        return f"NFC Card {self.card_uid} for {self.student_id}"


class AttendanceLog(models.Model):
    """
    Audit trail for all attendance operations.
    
    This model maintains a comprehensive log of all attendance-related
    operations including method used, success status, and additional details.
    """
    student_id: Optional['Student'] = models.ForeignKey(
        Student, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='attendance_logs'
    )
    class_id: Optional['Class'] = models.ForeignKey(
        Class, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='attendance_logs'
    )
    method_id: Optional['AttendanceMethod'] = models.ForeignKey(
        AttendanceMethod, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='attendance_logs'
    )
    session: Optional['ClassSession'] = models.ForeignKey(
        ClassSession, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='attendance_logs'
    )
    details: dict = models.JSONField(default=dict, blank=True)
    timestamp: datetime.datetime = models.DateTimeField(default=timezone.now, db_index=True)
    success: bool = models.BooleanField(default=True)
    ip_address: Optional[str] = models.CharField(max_length=45, null=True, blank=True)
    device_info: Optional[str] = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_attendancelog'
        verbose_name = 'Attendance Log'
        verbose_name_plural = 'Attendance Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['student_id', 'timestamp'], name='log_student_time_idx'),
            models.Index(fields=['class_id', 'timestamp'], name='log_class_time_idx'),
            models.Index(fields=['method_id', 'timestamp'], name='log_method_time_idx'),
            models.Index(fields=['success', 'timestamp'], name='log_success_time_idx'),
        ]
    
    def __str__(self) -> str:
        student_name = self.student_id if self.student_id else "Unknown"
        return f"Attendance Log: {student_name} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"