# Python standard libraries
import os
import json
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List

# Third-party libraries
import jwt
import cv2
import numpy as np
import face_recognition

# Django imports
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.base import ContentFile

# Django REST framework imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

# Local app imports
from .models import User, Role, Admin, Student, Class, Attendance
from .serializers import UserSerializer, RoleSerializer, AdminSerializer, StudentSerializer, ClassSerializer, AttendanceSerializer

class RegisterView(APIView):
    def post(self, request: HttpRequest) -> Response:
        # Extract only the necessary fields for the UserSerializer
        user_data: Dict[str, Any] = {
            'name': request.data.get('first_name'),
            'username': request.data.get('username'),
            'password': request.data.get('password')
        }

        # Validate and save the user data
        user_serializer = UserSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = user_serializer.save()

        # Prepare student data
        student_data = request.data.copy()
        student_data['user'] = user.id

        # Decode the base64 image and save it as a file
        student_img_base64 = student_data.get('student_img')
        if student_img_base64:
            try:
                format, imgstr = student_img_base64.split(';base64,')
                ext = format.split('/')[-1]
                img_data = ContentFile(base64.b64decode(imgstr), name=f'user_{user.id}.{ext}')
                student_data['student_img'] = img_data
            except Exception as e:
                return Response({'error': 'Invalid image format'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save the student data
        student_serializer = StudentSerializer(data=student_data, context={'request': request})
        if not student_serializer.is_valid():
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student = student_serializer.save()

        # Combine the response data
        response_data: Dict[str, Any] = {
            'user': user_serializer.data,
            'student': student_serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    
class LoginView(APIView):
    def post(self, request: HttpRequest) -> Response:
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        payload: Dict[str, Any] = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(
            key='jwt',
            value=token,
            httponly=True, 
            samesite='Lax', 
            secure=True, 
            expires=datetime.now(timezone.utc) + timedelta(minutes=60)  # Optional: exact expiry time
        )   
        response.data: Dict[str, Any] = {
            'username': user.username,
            'user_id': user.id,
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
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('Unauthenticated')

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


class StudentDashboardView(APIView):
    def get(self, response, user_id):
        student = get_object_or_404(Student, user_id=user_id)
        student_class = student.student_class
        attendance_records = Attendance.objects.filter(student=student).order_by('-date_time')
        total_present = attendance_records.filter(status='Present').count()
        total_absent = attendance_records.filter(status='Absent').count()
        total_late = attendance_records.filter(status='Late').count()
        total_days = total_present + total_absent + total_late
        overall_percentage = round((total_present / total_days) * 100, 2) if total_days > 0 else 0
        attendance_breakdown = [
            {"name": "Present", "value": total_present},
            {"name": "Absent", "value": total_absent},
            {"name": "Late", "value": total_late},
        ]
        recent_attendance = [
            {"date": att.date_time.strftime("%Y-%m-%d"), "status": att.status}
            for att in attendance_records[:5]
        ]
        attendance_trend = [
            {
                "date": att.date_time.strftime("%Y-%m-%d"),
                "attendance": 1 if att.status == 'Present' else (0.5 if att.status == 'Late' else 0),
            }
            for att in attendance_records[:7]
        ]
        classmates = Student.objects.filter(student_class_id=student_class)
        total_classmates = classmates.count()
        classmate_attendance = []
        for classmate in classmates:
            classmate_records = Attendance.objects.filter(student=classmate)
            classmate_present = classmate_records.filter(status='Present').count()
            classmate_absent = classmate_records.filter(status='Absent').count()
            classmate_late = classmate_records.filter(status='Late').count()
            classmate_total_days = classmate_present + classmate_absent + classmate_late
            classmate_percentage = (classmate_present / classmate_total_days) * 100 if classmate_total_days > 0 else 0
            classmate_attendance.append((classmate.user_id, classmate_percentage))
        classmate_attendance.sort(key=lambda x: x[1], reverse=True)
        student_rank = next((index for index, (id, _) in enumerate(classmate_attendance) if id == student.user_id), None)
        student_rank_actual = student_rank + 1 if student_rank is not None else total_classmates
        class_ranking = {
            "rank": student_rank_actual,
            "total": total_classmates,
        }
        from django.utils import timezone
        last_check_in = (
            
            timezone.localtime(attendance_records[0].date_time).strftime("%Y-%m-%d %I:%M %p") if attendance_records else "N/A"
        )
        data = {
            "id": student.user.id,
            "first_name": student.first_name,
            "middle_name": student.middle_name if student.middle_name else "",
            "last_name": student.last_name,
            "student_img": student.student_img.url if student.student_img else "/placeholder.svg",
            "student_class": {
                "name": student_class.name,
                "section": student_class.section,
                "semester": student_class.semester,
                "year": student_class.year,
            },
            "attendance": {
                "overall_percentage": overall_percentage,
                "total_present": total_present,
                "total_absent": total_absent,
                "total_late": total_late,
                "breakdown": attendance_breakdown,
            },
            "recent_attendance": recent_attendance,
            "attendance_trend": attendance_trend,
            "class_ranking": class_ranking,
            "last_check_in": last_check_in,
        }
        return Response(data)



def prepare_image(image: np.ndarray) -> np.ndarray:
    """Optimized image preprocessing"""
    image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb

def verify_faces(ref_img: np.ndarray, uploaded_img: np.ndarray, tolerance: float = 0.6) -> bool:
    """Face verification using face_recognition"""
    try:
        # Get face encodings
        ref_encodings = face_recognition.face_encodings(ref_img)
        uploaded_encodings = face_recognition.face_encodings(uploaded_img)
        
        if not ref_encodings or not uploaded_encodings:
            return False
            
        # Compare faces
        results = face_recognition.compare_faces(
            [ref_encodings[0]], 
            uploaded_encodings[0], 
            tolerance=tolerance
        )
        return results[0]
    except Exception as e:
        return False

@method_decorator(csrf_exempt, name='dispatch')
class FaceVerification(View):
    def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body)
            student_id = data.get('student_id')
            image_data = data.get('image_data')

            if not student_id or not image_data:
                return JsonResponse({'error': 'Missing student_id or image_data'}, status=400)

            # Get student
            try:
                student = Student.objects.get(user_id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({'error': 'Student not found'}, status=404)

            # Process images
            try:
                # Decode uploaded image
                nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
                uploaded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if uploaded is None:
                    return JsonResponse({'error': 'Invalid image data'}, status=400)
                
                processed_upload = prepare_image(uploaded)

                # Load and process reference image
                ref_img = cv2.imread(student.student_img.path)
                if ref_img is None:
                    return JsonResponse({'error': 'Failed to load reference image'}, status=400)
                
                processed_ref = prepare_image(ref_img)
            except Exception as e:
                return JsonResponse({'error': f'Image processing error: {str(e)}'}, status=400)

            # Verify faces
            verified = verify_faces(processed_ref, processed_upload)

            # Record attendance
            status = Attendance.PRESENT if verified else Attendance.ABSENT
            if verified:
                Attendance.objects.create(
                    student=student,
                    status=status,
                    date_time=timezone.now()
                )

            # Build response
            response_data = {
                'verified': bool(verified),
                'status': status
            }
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

# CRUD Views for Role
class RoleListCreateView(APIView):
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleUpdateDeleteView(APIView):
    def get(self, request, role_id):
        role = get_object_or_404(Role, id=role_id)
        serializer = RoleSerializer(role)
        return Response(serializer.data)
    
    def put(self, request, role_id):
        role = get_object_or_404(Role, id=role_id)
        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, role_id):
        role = get_object_or_404(Role, id=role_id)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# CRUD Views for Admin
class AdminListCreateView(APIView):
    def get(self, request):
        admins = Admin.objects.all()
        serializer = AdminSerializer(admins, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminUpdateDeleteView(APIView):
    def get(self, request, user_id):
        admin = get_object_or_404(Admin, user_id=user_id)
        serializer = AdminSerializer(admin)
        return Response(serializer.data)
    
    def put(self, request, user_id):
        admin = get_object_or_404(Admin, user_id=user_id)
        serializer = AdminSerializer(admin, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        admin = get_object_or_404(Admin, user_id=user_id)
        admin.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# CRUD Views for Class
class ClassListCreateView(APIView):
    def get(self, request):
        classes = Class.objects.all()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClassUpdateDeleteView(APIView):
    def get(self, request, class_id):
        class_obj = get_object_or_404(Class, class_id=class_id)
        serializer = ClassSerializer(class_obj)
        return Response(serializer.data)
    
    def put(self, request, class_id):
        class_obj = get_object_or_404(Class, class_id=class_id)
        serializer = ClassSerializer(class_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, class_id):
        class_obj = get_object_or_404(Class, class_id=class_id)
        class_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# CRUD Views for Attendance
class AttendanceListCreateView(APIView):
    def get(self, request):
        attendance = Attendance.objects.all()
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceUpdateDeleteView(APIView):
    def get(self, request, attendance_id):
        attendance = get_object_or_404(Attendance, id=attendance_id)
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    def put(self, request, attendance_id):
        attendance = get_object_or_404(Attendance, id=attendance_id)
        serializer = AttendanceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, attendance_id):
        attendance = get_object_or_404(Attendance, id=attendance_id)
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Additional Utility Views
class AttendanceMarkView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        status = request.data.get('status', 'Present')
        
        if not student_id:
            return Response({'error': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        student = get_object_or_404(Student, user_id=student_id)
        attendance = Attendance.objects.create(student=student, status=status)
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StudentAttendanceView(APIView):
    def get(self, request, user_id):
        student = get_object_or_404(Student, user_id=user_id)
        attendance = Attendance.objects.filter(student=student).order_by('-date_time')
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
        
