"""
Django Views for the Admin Application.

This module provides admin views with proper type hints, logging,
comprehensive error handling, and follows professional coding practices.
"""

# Django core imports
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date

# Python standard libraries
import json
import csv
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List

# Django REST framework imports
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

# App models and serializers
from api.models import Admin, Class, Student, Attendance
from .serializers import (
    UserSerializer,
    ClassSerializer,
    StudentSerializer,
    AttendanceSerializer,
)
from .models import AdminUser

# Django ORM utilities
from django.db.models import Count, Prefetch

# Configure logger for this module
logger: logging.Logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    API View for admin user registration.
    """
    
    def post(self, request) -> Response:
        """
        Register a new admin user.
        
        Args:
            request: HTTP request with registration data.
            
        Returns:
            Response with created user data.
        """
        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        logger.info(f"Admin user registered: {user_serializer.data.get('username')}")
        return Response(user_serializer.data)


class LoginView(APIView):
    """
    API View for admin authentication.
    """
    
    def post(self, request) -> Response:
        """
        Authenticate admin user and generate JWT token.
        
        Args:
            request: HTTP request with login credentials.
            
        Returns:
            Response with JWT token and user info.
        """
        username: str | None = request.data.get('username')
        password: str | None = request.data.get('password')
        
        user: AdminUser | None = AdminUser.objects.filter(username=username).first()
        
        if user is None:
            logger.warning(f"Login attempt for non-existent admin: {username}")
            raise AuthenticationFailed('User not found')
            
        if not user.check_password(password):
            logger.warning(f"Invalid password attempt for admin: {username}")
            raise AuthenticationFailed('Incorrect password')
        
        payload: Dict[str, Any] = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
            'iat': datetime.now(timezone.utc)
        }
        
        token: str = jwt.encode(payload, 'secret', algorithm='HS256')
        
        response: Response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'username': user.username,
            'jwt': token
        }
        
        logger.info(f"Admin logged in: user_id={user.id}")
        return response


class UserView(APIView):
    """
    API View for retrieving current admin user information.
    """
    
    def get(self, request) -> Response:
        """
        Retrieve current authenticated admin's information.
        
        Args:
            request: HTTP request with JWT token.
            
        Returns:
            Response with user data.
        """
        token: str | None = request.COOKIES.get('jwt')
        
        if not token:
            logger.warning("Admin authentication attempt without token")
            raise AuthenticationFailed('Unauthenticated')
            
        try:
            payload: Dict[str, Any] = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            logger.warning("Admin JWT token expired")
            raise AuthenticationFailed('Unauthenticated')
            
        user: AdminUser | None = AdminUser.objects.filter(id=payload['id']).first()
        serializer: UserSerializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    """
    API View for admin logout.
    """
    
    def post(self, request) -> Response:
        """
        Logout admin by clearing JWT cookie.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response with logout confirmation.
        """
        response: Response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'success'}
        return response


class ClassListView(generics.ListAPIView):
    """
    API View for listing all classes.
    """
    
    queryset = Class.objects.all()
    serializer_class = ClassSerializer


class ClassCreateView(generics.CreateAPIView):
    """
    API View for creating new classes.
    """
    
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    
    def perform_create(self, serializer) -> None:
        """
        Save the class with associated admin.
        
        Args:
            serializer: The class serializer instance.
        """
        admin_id: int | None = self.request.data.get('admin')
        
        if admin_id:
            admin: Admin = get_object_or_404(Admin, user_id=admin_id)
            serializer.save(admin=admin)
            logger.info(f"Class created: {serializer.data}")
        else:
            serializer.save()


class ClassUpdateView(generics.RetrieveUpdateAPIView):
    """
    API View for updating classes.
    """
    
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    lookup_field: str = "class_id"


class ClassDeleteView(generics.DestroyAPIView):
    """
    API View for deleting classes.
    """
    
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    lookup_field: str = "class_id"
    
    def delete(self, request, *args, **kwargs) -> Response:
        """
        Delete a class and log the action.
        
        Args:
            request: HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            Response with no content.
        """
        class_id: int = kwargs.get('class_id', 0)
        logger.info(f"Class deleted: class_id={class_id}")
        return super().delete(request, *args, **kwargs)


class ClassCountView(APIView):
    """
    API View for getting class count.
    """
    
    def get(self, request) -> Response:
        """
        Get total number of classes.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response with class count.
        """
        count: int = Class.objects.count()
        return Response({"total_classes": count}, status=status.HTTP_200_OK)


class StudentListView(generics.ListAPIView):
    """
    API View for listing all students.
    """
    
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentCreateView(generics.CreateAPIView):
    """
    API View for creating new students.
    """
    
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentCountView(APIView):
    """
    API View for getting student count.
    """
    
    def get(self, request) -> Response:
        """
        Get total number of students.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response with student count.
        """
        count: int = Student.objects.count()
        return Response({"total_students": count}, status=status.HTTP_200_OK)


class StudentUpdateView(generics.RetrieveUpdateAPIView):
    """
    API View for updating students.
    """
    
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field: str = "user_id"
    
    def update(self, request, *args, **kwargs) -> Response:
        """
        Update a student with logging.
        
        Args:
            request: HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            Response with updated student data.
        """
        logger.debug(f"Student update request data: {request.data}")
        return super().update(request, *args, **kwargs)


class StudentDeleteView(generics.DestroyAPIView):
    """
    API View for deleting students.
    """
    
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field: str = "user_id"
    
    def delete(self, request, *args, **kwargs) -> Response:
        """
        Delete a student and log the action.
        
        Args:
            request: HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            Response with no content.
        """
        user_id: int = kwargs.get('user_id', 0)
        logger.info(f"Student deleted: user_id={user_id}")
        return super().delete(request, *args, **kwargs)


class AttendanceListView(generics.ListAPIView):
    """
    API View for listing all attendance records.
    """
    
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class AttendanceUpdateView(generics.RetrieveUpdateAPIView):
    """
    API View for updating attendance records.
    """
    
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    lookup_field: str = "attendance_id"


class AttendanceReportView(APIView):
    """
    API View for generating attendance reports.
    """
    
    def post(self, request) -> Response:
        """
        Generate attendance report for a class within a date range.
        
        Args:
            request: HTTP request with classId, startDate, and endDate.
            
        Returns:
            Response with attendance report data.
        """
        class_id: int | None = request.data.get("classId")
        start_date = parse_date(request.data.get("startDate"))
        end_date = parse_date(request.data.get("endDate"))
        
        if not class_id or not start_date or not end_date:
            return Response(
                {"error": "Missing parameters"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            class_obj: Class = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response(
                {"error": "Class not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        students: List[Student] = list(
            Student.objects.filter(student_class=class_obj)
        )
        
        attendance_records: List[Attendance] = list(
            Attendance.objects.filter(
                student__in=students,
                date_time__date__range=(start_date, end_date)
            )
        )

        report: List[Dict[str, Any]] = []
        
        for student in students:
            student_records: List[Attendance] = [
                att for att in attendance_records if att.student == student
            ]
            total: int = len(student_records)
            present: int = sum(1 for att in student_records if att.status == 'Present')
            absent: int = sum(1 for att in student_records if att.status == 'Absent')
            late: int = sum(1 for att in student_records if att.status == 'Late')
            attendance_rate: float = (present / total * 100) if total else 0

            report.append({
                "student": (
                    f"{student.first_name} "
                    f"{student.middle_name or ''} "
                    f"{student.last_name}"
                ).strip(),
                "totalRecords": total,
                "present": present,
                "absent": absent,
                "late": late,
                "attendanceRate": round(attendance_rate, 2),
            })

        total_records: int = len(attendance_records)
        total_present: int = sum(
            1 for att in attendance_records if att.status == 'Present'
        )
        total_absent: int = sum(
            1 for att in attendance_records if att.status == 'Absent'
        )
        total_late: int = sum(
            1 for att in attendance_records if att.status == 'Late'
        )

        overall_rate: float = (
            (total_present / total_records * 100) if total_records else 0
        )

        return Response({
            "class": f"{class_obj.name} - {class_obj.section}",
            "semester": class_obj.semester,
            "year": class_obj.year,
            "dateRange": {
                "start": start_date,
                "end": end_date
            },
            "totalStudents": len(students),
            "totalRecords": total_records,
            "present": total_present,
            "absent": total_absent,
            "late": total_late,
            "overallAttendanceRate": round(overall_rate, 2),
            "studentReport": report
        }, status=status.HTTP_200_OK)


class AttendanceExportView(APIView):
    """
    API View for exporting attendance data.
    """
    
    def post(self, request) -> Response:
        """
        Export attendance data (placeholder).
        
        Args:
            request: HTTP request.
            
        Returns:
            Response indicating export functionality.
        """
        return Response(
            {"message": "Export functionality not implemented yet"},
            status=status.HTTP_200_OK
        )


class RecentAttendanceView(View):
    """
    View for retrieving recent attendance records.
    """
    
    def get(self, request) -> JsonResponse:
        """
        Get recent attendance records.
        
        Args:
            request: HTTP request.
            
        Returns:
            JsonResponse with recent attendance data.
        """
        recent_attendance: List[Attendance] = list(
            Attendance.objects.order_by("-date_time")[:10]
        )
        
        attendance_data: List[Dict[str, Any]] = []
        for record in recent_attendance:
            attendance_data.append({
                "id": record.id,
                "status": record.status,
                "first_name": record.student.first_name,
                "last_name": record.student.last_name,
                "username": record.student.user.username
            })
            
        return JsonResponse(attendance_data, safe=False)


class AttendanceTrendView(View):
    """
    View for retrieving attendance trends.
    """
    
    def get(self, request) -> JsonResponse:
        """
        Get attendance trend data.
        
        Args:
            request: HTTP request.
            
        Returns:
            JsonResponse with attendance trends.
        """
        trend_data: List[Dict[str, Any]] = list(
            Attendance.objects.values("status")
            .annotate(total=Count("status"))
            .order_by("-total")
        )
        return JsonResponse(trend_data, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class AttendanceReportView(View):
    """
    View for generating detailed attendance reports.
    """
    
    def post(self, request) -> JsonResponse:
        """
        Generate detailed attendance report with daily breakdown.
        
        Args:
            request: HTTP request with classId, startDate, and endDate.
            
        Returns:
            JsonResponse with detailed report data.
        """
        try:
            data: Dict[str, Any] = json.loads(request.body)
            class_id: int | None = data.get("classId")
            start_date_str: str | None = data.get("startDate")
            end_date_str: str | None = data.get("endDate")

            if not all([class_id, start_date_str, end_date_str]):
                return JsonResponse(
                    {"error": "Missing parameters"}, 
                    status=400
                )

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            class_obj: Class = Class.objects.get(class_id=class_id)
            total_students: int = Student.objects.filter(
                student_class=class_obj
            ).count()

            # Get all relevant attendance records
            attendance_records: List[Attendance] = list(
                Attendance.objects.filter(
                    student__student_class=class_obj,
                    date_time__date__range=[start_date, end_date]
                ).select_related('student')
            )

            # Daily Breakdown
            daily_data: Dict[str, Dict[str, Any]] = {}
            for record in attendance_records:
                date_str: str = record.date_time.date().isoformat()
                
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        "present": 0,
                        "late": 0,
                        "totalStudents": total_students,
                    }
                    
                if record.status == Attendance.PRESENT:
                    daily_data[date_str]["present"] += 1
                elif record.status == Attendance.LATE:
                    daily_data[date_str]["late"] += 1

            # Calculate daily stats
            daily_breakdown: List[Dict[str, Any]] = []
            total_present: int = 0
            total_late: int = 0
            total_absent: int = 0
            
            for date_str, data_dict in daily_data.items():
                absent: int = (
                    data_dict["totalStudents"] 
                    - (data_dict["present"] + data_dict["late"])
                )
                attendance_rate: float = (
                    ((data_dict["present"] + data_dict["late"]) 
                     / data_dict["totalStudents"] * 100)
                    if data_dict["totalStudents"] else 0
                )
                
                daily_breakdown.append({
                    "date": date_str,
                    "present": data_dict["present"],
                    "late": data_dict["late"],
                    "absent": absent,
                    "attendanceRate": round(attendance_rate, 2),
                })

                total_present += data_dict["present"]
                total_late += data_dict["late"]
                total_absent += absent

            # Summary Statistics
            total_days: int = len(daily_data)
            total_possible_attendance: int = (
                total_students * total_days if total_days else 0
            )
            overall_rate: float = (
                ((total_present + total_late) 
                 / total_possible_attendance * 100)
                if total_possible_attendance else 0
            )

            summary: Dict[str, Any] = {
                "totalDays": total_days,
                "totalStudents": total_students,
                "totalPresent": total_present,
                "totalLate": total_late,
                "totalAbsent": total_absent,
                "overallAttendanceRate": round(overall_rate, 2),
            }

            # Student-wise Statistics
            students: List[Student] = list(
                Student.objects.filter(student_class=class_obj).prefetch_related(
                    Prefetch(
                        'attendance_set',
                        queryset=Attendance.objects.filter(
                            date_time__date__range=[start_date, end_date]
                        ),
                        to_attr='filtered_attendance'
                    )
                )
            )

            student_reports: List[Dict[str, Any]] = []
            for student in students:
                present: int = sum(
                    1 for a in student.filtered_attendance 
                    if a.status == Attendance.PRESENT
                )
                late: int = sum(
                    1 for a in student.filtered_attendance 
                    if a.status == Attendance.LATE
                )
                absent_days: int = total_days - (present + late)
                student_rate: float = (
                    ((present + late) / total_days * 100) 
                    if total_days else 0
                )

                student_reports.append({
                    "id": student.user_id,
                    "name": f"{student.first_name} {student.last_name}",
                    "present": present,
                    "late": late,
                    "absent": absent_days,
                    "attendanceRate": round(student_rate, 2),
                })

            return JsonResponse({
                "summary": summary,
                "dailyBreakdown": daily_breakdown,
                "students": student_reports,
            }, safe=False)

        except ValueError:
            return JsonResponse(
                {"error": "Invalid date format"}, 
                status=400
            )
        except Class.DoesNotExist:
            return JsonResponse(
                {"error": "Class not found"}, 
                status=404
            )
        except Exception as e:
            logger.error(f"Attendance report error: {e}")
            return JsonResponse(
                {"error": str(e)}, 
                status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class AttendanceExportView(View):
    """
    View for exporting attendance data to CSV.
    """
    
    def post(self, request) -> HttpResponse:
        """
        Export attendance data as CSV file.
        
        Args:
            request: HTTP request with classId, startDate, and endDate.
            
        Returns:
            CSV file response.
        """
        try:
            data: Dict[str, Any] = json.loads(request.body)
            class_id: int | None = data.get("classId")
            start_date_str: str | None = data.get("startDate")
            end_date_str: str | None = data.get("endDate")

            if not all([class_id, start_date_str, end_date_str]):
                return JsonResponse(
                    {"error": "Missing parameters"}, 
                    status=400
                )

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            class_obj: Class = Class.objects.get(class_id=class_id)
            students: List[Student] = list(
                Student.objects.filter(student_class=class_obj)
            )
            attendance_records: List[Attendance] = list(
                Attendance.objects.filter(
                    student__in=students,
                    date_time__date__range=[start_date, end_date]
                )
            )

            response: HttpResponse = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                'attachment; filename="attendance_report.csv"'
            )
            writer = csv.writer(response)
            writer.writerow(["Student Name", "Class", "Date", "Status"])
            
            for record in attendance_records:
                writer.writerow([
                    f"{record.student.first_name} {record.student.last_name}",
                    f"{class_obj.name} - {class_obj.section}",
                    record.date_time.strftime("%Y-%m-%d"),
                    record.status
                ])
                
            logger.info(
                f"Attendance exported: class_id={class_id}, "
                f"records={len(attendance_records)}"
            )
            return response
            
        except Class.DoesNotExist:
            return JsonResponse(
                {"error": "Class not found"}, 
                status=404
            )
        except ValueError:
            return JsonResponse(
                {"error": "Invalid date format"}, 
                status=400
            )
        except Exception as e:
            logger.error(f"Attendance export error: {e}")
            return JsonResponse(
                {"error": str(e)}, 
                status=500
            )
