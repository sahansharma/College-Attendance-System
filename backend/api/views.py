"""
Django REST Framework Views for the College Attendance System API.

This module provides API views with proper type hints, logging,
comprehensive error handling, and follows professional coding practices.
"""

# Python standard libraries
import os
import json
import base64
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, TypeVar

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
from django.utils import timezone as django_timezone

# Django REST framework imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

# Local app imports
from .models import User, Role, Admin, Student, Class, Attendance
from .serializers import (
    UserSerializer, 
    RoleSerializer, 
    AdminSerializer, 
    StudentSerializer, 
    ClassSerializer, 
    AttendanceSerializer
)

# Configure logger for this module
logger: logging.Logger = logging.getLogger(__name__)

# Type variable for generic view responses
V = TypeVar('V')


class RegisterView(APIView):
    """
    API View for user registration.
    
    Handles student registration with user creation and image upload.
    """
    
    def post(self, request: HttpRequest) -> Response:
        """
        Register a new student with user account and image.
        
        Args:
            request: HTTP request containing registration data.
            
        Returns:
            Response with created user and student data.
            
        Raises:
            ValidationError: If registration data is invalid.
        """
        # Extract only the necessary fields for the UserSerializer
        user_data: Dict[str, Any] = {
            'name': request.data.get('first_name'),
            'username': request.data.get('username'),
            'password': request.data.get('password')
        }

        # Validate and save the user data
        user_serializer = UserSerializer(data=user_data)
        if not user_serializer.is_valid():
            logger.warning(f"User registration validation failed: {user_serializer.errors}")
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
                logger.error(f"Image processing error during registration: {e}")
                return Response({'error': 'Invalid image format'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save the student data
        student_serializer = StudentSerializer(data=student_data, context={'request': request})
        if not student_serializer.is_valid():
            logger.warning(f"Student registration validation failed: {student_serializer.errors}")
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student = student_serializer.save()

        # Combine the response data
        response_data: Dict[str, Any] = {
            'user': user_serializer.data,
            'student': student_serializer.data
        }
        
        logger.info(f"User registered successfully: user_id={user.id}")
        return Response(response_data, status=status.HTTP_201_CREATED)

    
class LoginView(APIView):
    """
    API View for user authentication.
    
    Handles user login and JWT token generation.
    """
    
    def post(self, request: HttpRequest) -> Response:
        """
        Authenticate user and generate JWT token.
        
        Args:
            request: HTTP request containing login credentials.
            
        Returns:
            Response with JWT token and user info.
            
        Raises:
            AuthenticationFailed: If credentials are invalid.
        """
        username: str | None = request.data.get('username')
        password: str | None = request.data.get('password')
        
        user: User | None = User.objects.filter(username=username).first()
        
        if user is None:
            logger.warning(f"Login attempt for non-existent user: {username}")
            raise AuthenticationFailed('User not found')
            
        if not user.check_password(password):
            logger.warning(f"Invalid password attempt for user: {username}")
            raise AuthenticationFailed('Incorrect password')
        
        # Generate JWT token
        payload: Dict[str, Any] = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
            'iat': datetime.now(timezone.utc)
        }
        
        token: str = jwt.encode(payload, 'secret', algorithm='HS256')
        
        response: Response = Response()
        response.set_cookie(
            key='jwt',
            value=token,
            httponly=True, 
            samesite='Lax', 
            secure=True, 
            expires=datetime.now(timezone.utc) + timedelta(minutes=60)
        )
        
        response.data: Dict[str, Any] = {
            'username': user.username,
            'user_id': user.id,
            'jwt': token
        }
        
        logger.info(f"User logged in successfully: user_id={user.id}")
        return response
    
    
class UserView(APIView):
    """
    API View for retrieving current user information.
    
    Requires valid JWT token for authentication.
    """
    
    def get(self, request: HttpRequest) -> Response:
        """
        Retrieve current authenticated user's information.
        
        Args:
            request: HTTP request with JWT token.
            
        Returns:
            Response with user data.
            
        Raises:
            AuthenticationFailed: If token is invalid or expired.
        """
        token: str | None = request.COOKIES.get('jwt')

        if not token:
            logger.warning("Authentication attempt without token")
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload: Dict[str, Any] = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            raise AuthenticationFailed('Unauthenticated')
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise AuthenticationFailed('Unauthenticated')

        user: User | None = User.objects.filter(id=payload['id']).first()
        
        if not user:
            logger.warning(f"User not found for token payload: {payload.get('id')}")
            raise AuthenticationFailed('Unauthenticated')

        serializer = UserSerializer(user)
        return Response(serializer.data)
        
        
class LogoutView(APIView):
    """
    API View for user logout.
    
    Clears the JWT cookie.
    """
    
    def post(self, request: HttpRequest) -> Response:
        """
        Logout user by clearing JWT cookie.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response with logout confirmation.
        """
        response: Response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'success'}
        return response


class StudentDashboardView(APIView):
    """
    API View for student dashboard data.
    
    Provides attendance statistics and rankings.
    """
    
    def get(self, request: HttpRequest, user_id: int) -> Response:
        """
        Retrieve dashboard data for a specific student.
        
        Args:
            request: HTTP request.
            user_id: The ID of the student.
            
        Returns:
            Response with dashboard data including attendance statistics.
        """
        student: Student = get_object_or_404(Student, user_id=user_id)
        student_class: Class = student.student_class
        
        attendance_records: List[Attendance] = list(
            Attendance.objects.filter(student=student).order_by('-date_time')
        )
        
        total_present: int = sum(1 for att in attendance_records if att.status == 'Present')
        total_absent: int = sum(1 for att in attendance_records if att.status == 'Absent')
        total_late: int = sum(1 for att in attendance_records if att.status == 'Late')
        total_days: int = total_present + total_absent + total_late
        
        overall_percentage: float = (
            round((total_present / total_days) * 100, 2) 
            if total_days > 0 else 0
        )
        
        attendance_breakdown: List[Dict[str, Any]] = [
            {"name": "Present", "value": total_present},
            {"name": "Absent", "value": total_absent},
            {"name": "Late", "value": total_late},
        ]
        
        recent_attendance: List[Dict[str, Any]] = [
            {
                "date": att.date_time.strftime("%Y-%m-%d"), 
                "status": att.status
            }
            for att in attendance_records[:5]
        ]
        
        attendance_trend: List[Dict[str, Any]] = [
            {
                "date": att.date_time.strftime("%Y-%m-%d"),
                "attendance": (
                    1 if att.status == 'Present' 
                    else (0.5 if att.status == 'Late' else 0)
                ),
            }
            for att in attendance_records[:7]
        ]
        
        classmates: List[Student] = list(
            Student.objects.filter(student_class_id=student_class)
        )
        total_classmates: int = len(classmates)
        
        classmate_attendance: List[tuple[int, float]] = []
        for classmate in classmates:
            classmate_records: List[Attendance] = list(
                Attendance.objects.filter(student=classmate)
            )
            classmate_present: int = sum(1 for att in classmate_records if att.status == 'Present')
            classmate_absent: int = sum(1 for att in classmate_records if att.status == 'Absent')
            classmate_late: int = sum(1 for att in classmate_records if att.status == 'Late')
            classmate_total_days: int = classmate_present + classmate_absent + classmate_late
            classmate_percentage: float = (
                (classmate_present / classmate_total_days) * 100 
                if classmate_total_days > 0 else 0
            )
            classmate_attendance.append((classmate.user_id, classmate_percentage))
        
        classmate_attendance.sort(key=lambda x: x[1], reverse=True)
        
        student_rank: int | None = next(
            (index for index, (id, _) in enumerate(classmate_attendance) 
             if id == student.user_id), 
            None
        )
        student_rank_actual: int = (
            student_rank + 1 if student_rank is not None else total_classmates
        )
        
        class_ranking: Dict[str, int] = {
            "rank": student_rank_actual,
            "total": total_classmates,
        }
        
        last_check_in: str = (
            django_timezone.localtime(attendance_records[0].date_time)
            .strftime("%Y-%m-%d %I:%M %p") 
            if attendance_records else "N/A"
        )
        
        data: Dict[str, Any] = {
            "id": student.user.id,
            "first_name": student.first_name,
            "middle_name": student.middle_name if student.middle_name else "",
            "last_name": student.last_name,
            "student_img": (
                student.student_img.url 
                if student.student_img else "/placeholder.svg"
            ),
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
    """
    Preprocess image for face recognition.
    
    Args:
        image: Input image as numpy array.
        
    Returns:
        Preprocessed image ready for face recognition.
    """
    image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb


def verify_faces(
    ref_img: np.ndarray, 
    uploaded_img: np.ndarray, 
    tolerance: float = 0.6
) -> bool:
    """
    Verify if two faces match using face_recognition library.
    
    Args:
        ref_img: Reference image containing known face.
        uploaded_img: Uploaded image to verify.
        tolerance: Similarity tolerance threshold (lower is stricter).
        
    Returns:
        True if faces match, False otherwise.
    """
    try:
        # Get face encodings
        ref_encodings: List[np.ndarray] = face_recognition.face_encodings(ref_img)
        uploaded_encodings: List[np.ndarray] = face_recognition.face_encodings(uploaded_img)
        
        if not ref_encodings or not uploaded_encodings:
            logger.warning("No faces detected in one or both images")
            return False
            
        # Compare faces
        results: List[bool] = face_recognition.compare_faces(
            [ref_encodings[0]], 
            uploaded_encodings[0], 
            tolerance=tolerance
        )
        return results[0]
        
    except Exception as e:
        logger.error(f"Face verification error: {e}")
        return False


@method_decorator(csrf_exempt, name='dispatch')
class FaceVerification(View):
    """
    View for face verification and attendance marking.
    
    Handles face recognition-based attendance verification.
    """
    
    def post(self, request: HttpRequest) -> JsonResponse:
        """
        Verify face and mark attendance.
        
        Args:
            request: HTTP request with student_id and image_data.
            
        Returns:
            JsonResponse with verification result.
        """
        try:
            # Parse JSON data
            data: Dict[str, Any] = json.loads(request.body)
            student_id: int | None = data.get('student_id')
            image_data: str | None = data.get('image_data')

            if not student_id or not image_data:
                return JsonResponse(
                    {'error': 'Missing student_id or image_data'}, 
                    status=400
                )

            # Get student
            try:
                student: Student = Student.objects.get(user_id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({'error': 'Student not found'}, status=404)

            # Process images
            try:
                # Decode uploaded image
                nparr: np.ndarray = np.frombuffer(
                    base64.b64decode(image_data), 
                    np.uint8
                )
                uploaded: np.ndarray | None = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if uploaded is None:
                    return JsonResponse(
                        {'error': 'Invalid image data'}, 
                        status=400
                    )
                
                processed_upload: np.ndarray = prepare_image(uploaded)

                # Load and process reference image
                ref_img: np.ndarray | None = cv2.imread(student.student_img.path)
                
                if ref_img is None:
                    return JsonResponse(
                        {'error': 'Failed to load reference image'}, 
                        status=400
                    )
                
                processed_ref: np.ndarray = prepare_image(ref_img)
                
            except Exception as e:
                logger.error(f"Image processing error: {e}")
                return JsonResponse(
                    {'error': f'Image processing error: {str(e)}'}, 
                    status=400
                )

            # Verify faces
            verified: bool = verify_faces(processed_ref, processed_upload)

            # Record attendance
            status_value: str = (
                Attendance.PRESENT if verified else Attendance.ABSENT
            )
            
            if verified:
                Attendance.objects.create(
                    student=student,
                    status=status_value,
                    date_time=django_timezone.now()
                )
                logger.info(f"Attendance marked for student_id={student_id}")

            # Build response
            response_data: Dict[str, Any] = {
                'verified': bool(verified),
                'status': status_value
            }
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Face verification error: {e}")
            return JsonResponse(
                {'error': f'Server error: {str(e)}'}, 
                status=500
            )


class RoleListCreateView(APIView):
    """
    API View for listing and creating Role entries.
    """
    
    def get(self, request: HttpRequest) -> Response:
        """
        List all roles.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response with list of roles.
        """
        roles: List[Role] = list(Role.objects.all())
        serializer: RoleSerializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    def post(self, request: HttpRequest) -> Response:
        """
        Create a new role.
        
        Args:
            request: HTTP request with role data.
            
        Returns:
            Response with created role data.
        """
        serializer: RoleSerializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Role created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleUpdateDeleteView(APIView):
    """
    API View for updating and deleting Role entries.
    """
    
    def get(self, request: HttpRequest, role_id: int) -> Response:
        """
        Retrieve a specific role.
        
        Args:
            request: HTTP request.
            role_id: The ID of the role.
            
        Returns:
            Response with role data.
        """
        role: Role = get_object_or_404(Role, id=role_id)
        serializer: RoleSerializer = RoleSerializer(role)
        return Response(serializer.data)
    
    def put(self, request: HttpRequest, role_id: int) -> Response:
        """
        Update a specific role.
        
        Args:
            request: HTTP request with updated role data.
            role_id: The ID of the role.
            
        Returns:
            Response with updated role data.
        """
        role: Role = get_object_or_404(Role, id=role_id)
        serializer: RoleSerializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Role updated: role_id={role_id}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request: HttpRequest, role_id: int) -> Response:
        """
        Delete a specific role.
        
        Args:
            request: HTTP request.
            role_id: The ID of the role.
            
        Returns:
            Response with no content.
        """
        role: Role = get_object_or_404(Role, id=role_id)
        role.delete()
        logger.info(f"Role deleted: role_id={role_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminListCreateView(APIView):
    """
    API View for listing and creating Admin entries.
    """
    
    def get(self, request: HttpRequest) -> Response:
        """
        List all admins.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response with list of admins.
        """
        admins: List[Admin] = list(Admin.objects.all())
        serializer: AdminSerializer = AdminSerializer(admins, many=True)
        return Response(serializer.data)
    
    def post(self, request: HttpRequest) -> Response:
        """
        Create a new admin.
        
        Args:
            request: HTTP request with admin data.
            
        Returns:
            Response with created admin data.
        """
        serializer: AdminSerializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Admin created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUpdateDeleteView(APIView):
    """
    API View for updating and deleting Admin entries.
    """
    
    def get(self, request: HttpRequest, user_id: int) -> Response:
        """
        Retrieve a specific admin.
        
        Args:
            request: HTTP request.
            user_id: The user ID of the admin.
            
        Returns:
            Response with admin data.
        """
        admin: Admin = get_object_or_404(Admin, user_id=user_id)
        serializer: AdminSerializer = AdminSerializer(admin)
        return Response(serializer.data)
    
    def put(self, request: HttpRequest, user_id: int) -> Response:
        """
        Update a specific admin.
        
        Args:
            request: HTTP request with updated admin data.
            user_id: The user ID of the admin.
            
        Returns:
            Response with updated admin data.
        """
        admin: Admin = get_object_or_404(Admin, user_id=user_id)
        serializer: AdminSerializer = AdminSerializer(admin, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Admin updated: user_id={user_id}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request: HttpRequest, user_id: int) -> Response:
        """
        Delete a specific admin.
        
        Args:
            request: HTTP request.
            user_id: The user ID of the admin.
            
        Returns:
            Response with no content.
        """
        admin: Admin = get_object_or_404(Admin, user_id=user_id)
        admin.delete()
        logger.info(f"Admin deleted: user_id={user_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassListCreateView(APIView):
    """
    API View for listing and creating Class entries.
    """
    
    def get(self, request: HttpRequest) -> Response:
        """
        List all classes.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response with list of classes.
        """
        classes: List[Class] = list(Class.objects.all())
        serializer: ClassSerializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)
    
    def post(self, request: HttpRequest) -> Response:
        """
        Create a new class.
        
        Args:
            request: HTTP request with class data.
            
        Returns:
            Response with created class data.
        """
        serializer: ClassSerializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Class created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClassUpdateDeleteView(APIView):
    """
    API View for updating and deleting Class entries.
    """
    
    def get(self, request: HttpRequest, class_id: int) -> Response:
        """
        Retrieve a specific class.
        
        Args:
            request: HTTP request.
            class_id: The class ID.
            
        Returns:
            Response with class data.
        """
        class_obj: Class = get_object_or_404(Class, class_id=class_id)
        serializer: ClassSerializer = ClassSerializer(class_obj)
        return Response(serializer.data)
    
    def put(self, request: HttpRequest, class_id: int) -> Response:
        """
        Update a specific class.
        
        Args:
            request: HTTP request with updated class data.
            class_id: The class ID.
            
        Returns:
            Response with updated class data.
        """
        class_obj: Class = get_object_or_404(Class, class_id=class_id)
        serializer: ClassSerializer = ClassSerializer(class_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Class updated: class_id={class_id}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request: HttpRequest, class_id: int) -> Response:
        """
        Delete a specific class.
        
        Args:
            request: HTTP request.
            class_id: The class ID.
            
        Returns:
            Response with no content.
        """
        class_obj: Class = get_object_or_404(Class, class_id=class_id)
        class_obj.delete()
        logger.info(f"Class deleted: class_id={class_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttendanceListCreateView(APIView):
    """
    API View for listing and creating Attendance entries.
    """
    
    def get(self, request: HttpRequest) -> Response:
        """
        List all attendance records.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response with list of attendance records.
        """
        attendance: List[Attendance] = list(Attendance.objects.all())
        serializer: AttendanceSerializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
    
    def post(self, request: HttpRequest) -> Response:
        """
        Create a new attendance record.
        
        Args:
            request: HTTP request with attendance data.
            
        Returns:
            Response with created attendance data.
        """
        serializer: AttendanceSerializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Attendance created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceUpdateDeleteView(APIView):
    """
    API View for updating and deleting Attendance entries.
    """
    
    def get(self, request: HttpRequest, attendance_id: int) -> Response:
        """
        Retrieve a specific attendance record.
        
        Args:
            request: HTTP request.
            attendance_id: The attendance ID.
            
        Returns:
            Response with attendance data.
        """
        attendance: Attendance = get_object_or_404(Attendance, id=attendance_id)
        serializer: AttendanceSerializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    def put(self, request: HttpRequest, attendance_id: int) -> Response:
        """
        Update a specific attendance record.
        
        Args:
            request: HTTP request with updated attendance data.
            attendance_id: The attendance ID.
            
        Returns:
            Response with updated attendance data.
        """
        attendance: Attendance = get_object_or_404(Attendance, id=attendance_id)
        serializer: AttendanceSerializer = AttendanceSerializer(
            attendance, 
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Attendance updated: attendance_id={attendance_id}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request: HttpRequest, attendance_id: int) -> Response:
        """
        Delete a specific attendance record.
        
        Args:
            request: HTTP request.
            attendance_id: The attendance ID.
            
        Returns:
            Response with no content.
        """
        attendance: Attendance = get_object_or_404(Attendance, id=attendance_id)
        attendance.delete()
        logger.info(f"Attendance deleted: attendance_id={attendance_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttendanceMarkView(APIView):
    """
    API View for manually marking attendance.
    """
    
    def post(self, request: HttpRequest) -> Response:
        """
        Mark attendance for a student.
        
        Args:
            request: HTTP request with student_id and status.
            
        Returns:
            Response with created attendance data.
        """
        student_id: int | None = request.data.get('student_id')
        status_value: str = request.data.get('status', 'Present')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student: Student = get_object_or_404(Student, user_id=student_id)
        attendance: Attendance = Attendance.objects.create(
            student=student, 
            status=status_value
        )
        serializer: AttendanceSerializer = AttendanceSerializer(attendance)
        logger.info(f"Attendance marked: student_id={student_id}, status={status_value}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentAttendanceView(APIView):
    """
    API View for retrieving attendance history for a student.
    """
    
    def get(self, request: HttpRequest, user_id: int) -> Response:
        """
        Retrieve attendance history for a specific student.
        
        Args:
            request: HTTP request.
            user_id: The user ID of the student.
            
        Returns:
            Response with list of attendance records.
        """
        student: Student = get_object_or_404(Student, user_id=user_id)
        attendance: List[Attendance] = list(
            Attendance.objects.filter(student=student).order_by('-date_time')
        )
        serializer: AttendanceSerializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
