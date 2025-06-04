from django.contrib import admin
from django.urls import path, include
from .views import (
    RegisterView, LoginView, UserView, LogoutView,
    ClassListView, ClassCreateView, ClassUpdateView, ClassDeleteView,
    StudentListView, StudentCountView, ClassCountView,
    AttendanceListView, AttendanceUpdateView,
    AttendanceReportView, AttendanceExportView,
    RecentAttendanceView, AttendanceTrendView, StudentCreateView,
    StudentUpdateView, StudentDeleteView
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("user", UserView.as_view(), name="user"),
    path("logout", LogoutView.as_view(), name="logout"),
    # path('student_dashboard/<int:user_id>/', StudentDashboardView.as_view(), name='student_dashboard'),

    # Classes
    path('classes/', ClassListView.as_view(), name='class-list'),  # GET: List all classes
    path('classes/create/', ClassCreateView.as_view(), name='class-create'),  # POST: Add a new class
    path('classes/<int:class_id>/', ClassUpdateView.as_view(), name='class-update'),  # PUT: Update class
    path('classes/<int:class_id>/delete/', ClassDeleteView.as_view(), name='class-delete'),  # DELETE: Remove class
    path('classes/count/', ClassCountView.as_view(), name='class-count'),  # GET: Total classes

    # Students
    path('students/', StudentListView.as_view(), name='student-list'),  # GET: List all students
    path('students/create/', StudentCreateView.as_view(), name='student-create'),  # POST: Add a student
    path('students/<int:user_id>/', StudentUpdateView.as_view(), name='student-update'),  # PUT: Update student
    path('students/<int:user_id>/delete/', StudentDeleteView.as_view(), name='student-delete'),  # DELETE: Remove student
    path('students/count/', StudentCountView.as_view(), name='student-count'),  # GET: Total students

    # Attendance
    path('attendance/', AttendanceListView.as_view(), name='attendance-list'),  # GET: List all attendance records
    path('attendance/<int:attendance_id>/', AttendanceUpdateView.as_view(), name='attendance-update'),  # PUT: Update attendance
    #path('attendance/bulk-update/', BulkAttendanceUpdateView.as_view(), name='attendance-bulk-update'),  # POST: Bulk update attendance
    path('attendance/recent/', RecentAttendanceView.as_view(), name='attendance-recent'),  # GET: Recent attendance
    path('attendance/trend/', AttendanceTrendView.as_view(), name='attendance-trend'),  # GET: Attendance trends

    # Reports
    path('reports/attendance/', AttendanceReportView.as_view(), name='attendance-report'),  # POST: Generate attendance report
    path('reports/export/', AttendanceExportView.as_view(), name='attendance-export'),  # POST: Export attendance report,
]