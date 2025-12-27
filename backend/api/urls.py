from django.contrib import admin
from django.urls import path, include
from .views import (
    RegisterView, LoginView, UserView, LogoutView, StudentDashboardView, FaceVerification,
    RoleListCreateView, RoleUpdateDeleteView,
    AdminListCreateView, AdminUpdateDeleteView,
    ClassListCreateView, ClassUpdateDeleteView,
    AttendanceListCreateView, AttendanceUpdateDeleteView,
    AttendanceMarkView, StudentAttendanceView
)

urlpatterns = [
    # Authentication
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("user", UserView.as_view(), name="user"),
    path("logout", LogoutView.as_view(), name="logout"),
    
    # Student specific views
    path('student_dashboard/<int:user_id>/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('student_attendance/<int:user_id>/', StudentAttendanceView.as_view(), name='student_attendance'),
    
    # Face verification
    path("face-verification", FaceVerification.as_view(), name="face_verification"),
    
    # Role CRUD operations
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:role_id>/', RoleUpdateDeleteView.as_view(), name='role-update-delete'),
    
    # Admin CRUD operations
    path('admins/', AdminListCreateView.as_view(), name='admin-list-create'),
    path('admins/<int:user_id>/', AdminUpdateDeleteView.as_view(), name='admin-update-delete'),
    
    # Class CRUD operations
    path('classes/', ClassListCreateView.as_view(), name='class-list-create'),
    path('classes/<int:class_id>/', ClassUpdateDeleteView.as_view(), name='class-update-delete'),
    
    # Attendance CRUD operations
    path('attendance/', AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('attendance/<int:attendance_id>/', AttendanceUpdateDeleteView.as_view(), name='attendance-update-delete'),
    path('attendance/mark/', AttendanceMarkView.as_view(), name='attendance-mark'),
]
