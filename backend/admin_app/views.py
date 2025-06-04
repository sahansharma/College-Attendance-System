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
import jwt
from datetime import datetime, timedelta, timezone

# Django REST framework imports
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

# App models and serializers
from api.models import  Admin, Class, Student, Attendance
from .serializers import (
    UserSerializer,
    ClassSerializer,
    StudentSerializer,
    AttendanceSerializer,
)
from .models import AdminUser

# Django ORM utilities
from django.db.models import Count, Prefetch

class RegisterView(APIView):
    def post(self, request):
        # Validate and save the user data
        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return Response(user_serializer.data)
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = AdminUser.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'username': user.username,
            'jwt': token
        }
        return response
    
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')
        user = AdminUser.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
        
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

class ClassListView(generics.ListAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

class ClassCreateView(generics.CreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    def perform_create(self, serializer):
        admin_id = self.request.data.get('admin')
        admin = get_object_or_404(Admin, user_id=admin_id)  # Admin's PK is user_id
        serializer.save(admin=admin)

class ClassUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    lookup_field = "class_id"

class ClassDeleteView(generics.DestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    lookup_field = "class_id"

class ClassCountView(APIView):
    def get(self, request):
        count = Class.objects.count()
        return Response({"total_classes": count}, status=status.HTTP_200_OK)

class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentCountView(APIView):
    def get(self, request):
        count = Student.objects.count()
        return Response({"total_students": count}, status=status.HTTP_200_OK)

class StudentUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = "user_id"
    def update(self, request, *args, **kwargs):
        print("Request data:", request.data)
        return super().update(request, *args, **kwargs)

class StudentDeleteView(generics.DestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = "user_id"

class AttendanceListView(generics.ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    lookup_field = "attendance_id"

class AttendanceReportView(APIView):
    def post(self, request):
        class_id = request.data.get("classId")
        start_date = parse_date(request.data.get("startDate"))
        end_date = parse_date(request.data.get("endDate"))
        if not class_id or not start_date or not end_date:
            return Response({"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Class not found"}, status=status.HTTP_404_NOT_FOUND)

        students = Student.objects.filter(student_class=class_obj)
        attendance_records = Attendance.objects.filter(
            student__in=students,
            date_time__date__range=(start_date, end_date)
        )

        report = []
        for student in students:
            student_records = attendance_records.filter(student=student)
            total = student_records.count()
            present = student_records.filter(status='Present').count()
            absent = student_records.filter(status='Absent').count()
            late = student_records.filter(status='Late').count()
            attendance_rate = (present / total * 100) if total else 0

            report.append({
                "student": f"{student.first_name} {student.middle_name or ''} {student.last_name}".strip(),
                "totalRecords": total,
                "present": present,
                "absent": absent,
                "late": late,
                "attendanceRate": round(attendance_rate, 2),
            })

        total_records = attendance_records.count()
        total_present = attendance_records.filter(status='Present').count()
        total_absent = attendance_records.filter(status='Absent').count()
        total_late = attendance_records.filter(status='Late').count()

        overall_rate = (total_present / total_records * 100) if total_records else 0

        return Response({
            "class": f"{class_obj.name} - {class_obj.section}",
            "semester": class_obj.semester,
            "year": class_obj.year,
            "dateRange": {
                "start": start_date,
                "end": end_date
            },
            "totalStudents": students.count(),
            "totalRecords": total_records,
            "present": total_present,
            "absent": total_absent,
            "late": total_late,
            "overallAttendanceRate": round(overall_rate, 2),
            "studentReport": report
        }, status=status.HTTP_200_OK)



class AttendanceExportView(APIView):
    def post(self, request):
        return Response({"message": "Export functionality not implemented yet"}, status=status.HTTP_200_OK)

class RecentAttendanceView(View):
    def get(self, request):
        recent_attendance = Attendance.objects.order_by("-date_time")[:10]
        attendance_data = []
        for record in recent_attendance:
            attendance_data.append({
                "id": record.id,
                "status": record.status,
                # "date_time": record.date_time.isoformat(),
                # "student_id": record.student_id,
                "first_name": record.student.first_name,
                "last_name": record.student.last_name,
                "username": record.student.user.username
            })
        return JsonResponse(attendance_data, safe=False)

# View for attendance trends
class AttendanceTrendView(View):
    def get(self, request):
        trend_data = (
            Attendance.objects.values("status")
            .annotate(total=Count("status"))
            .order_by("-total")
        )
        return JsonResponse(list(trend_data), safe=False)
    


@method_decorator(csrf_exempt, name="dispatch")
class AttendanceReportView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            class_id = data.get("classId")
            start_date_str = data.get("startDate")
            end_date_str = data.get("endDate")

            if not all([class_id, start_date_str, end_date_str]):
                return JsonResponse({"error": "Missing parameters"}, status=400)

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            class_obj = Class.objects.get(class_id=class_id)
            total_students = Student.objects.filter(student_class=class_obj).count()

            # Get all relevant attendance records
            attendance_records = Attendance.objects.filter(
                student__student_class=class_obj,
                date_time__date__range=[start_date, end_date]
            ).select_related('student')

            # Daily Breakdown
            daily_data = {}
            for record in attendance_records:
                date_str = record.date_time.date().isoformat()
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
            daily_breakdown = []
            total_present = total_late = total_absent = 0
            for date_str, data in daily_data.items():
                absent = data["totalStudents"] - (data["present"] + data["late"])
                attendance_rate = ((data["present"] + data["late"]) / data["totalStudents"] * 100) if data["totalStudents"] else 0
                
                daily_breakdown.append({
                    "date": date_str,
                    "present": data["present"],
                    "late": data["late"],
                    "absent": absent,
                    "attendanceRate": round(attendance_rate, 2),
                })

                total_present += data["present"]
                total_late += data["late"]
                total_absent += absent

            # Summary Statistics
            total_days = len(daily_data)
            total_possible_attendance = total_students * total_days if total_days else 0
            overall_rate = ((total_present + total_late) / total_possible_attendance * 100) if total_possible_attendance else 0

            summary = {
                "totalDays": total_days,
                "totalStudents": total_students,
                "totalPresent": total_present,
                "totalLate": total_late,
                "totalAbsent": total_absent,
                "overallAttendanceRate": round(overall_rate, 2),
            }

            # Student-wise Statistics
            students = Student.objects.filter(student_class=class_obj).prefetch_related(
                Prefetch('attendance_set', 
                        queryset=Attendance.objects.filter(
                            date_time__date__range=[start_date, end_date]),
                        to_attr='filtered_attendance')
            )

            student_reports = []
            for student in students:
                present = sum(1 for a in student.filtered_attendance if a.status == Attendance.PRESENT)
                late = sum(1 for a in student.filtered_attendance if a.status == Attendance.LATE)
                absent_days = total_days - (present + late)
                student_rate = ((present + late) / total_days * 100) if total_days else 0

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
            return JsonResponse({"error": "Invalid date format"}, status=400)
        except Class.DoesNotExist:
            return JsonResponse({"error": "Class not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class AttendanceExportView(View):
    def post(self, request):
        data = json.loads(request.body)
        class_id = data.get("classId")
        start_date = data.get("startDate")
        end_date = data.get("endDate")
        attendance_records = Attendance.objects.filter(
            class_id=class_id,
            date__range=[start_date, end_date]
        )
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="attendance_report.csv"'
        writer = csv.writer(response)
        writer.writerow(["Student", "Class", "Date", "Status"])
        for record in attendance_records:
            writer.writerow([record.student.user.username, record.class_id.name, record.date, record.status])
        return response
