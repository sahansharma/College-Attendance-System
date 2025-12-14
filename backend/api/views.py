# Python standard libraries
import os
import json
import base64
from datetime import datetime, timedelta, timezone

# Third-party libraries
import jwt
import cv2
import numpy as np
import face_recognition

# Django imports
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.files.base import ContentFile

# Django REST framework imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

# Local app imports
from .models import User, Student, Attendance
from .serializers import UserSerializer, StudentSerializer

class RegisterView(APIView):
    def post(self, request):
        # Extract only the necessary fields for the UserSerializer
        user_data = {
            'name': request.data.get('first_name'),
            'username': request.data.get('username'),
            'password': request.data.get('password')
        }
        print("🔧 Data to UserSerializer:")
        print(user_data)

        # Validate and save the user data
        user_serializer = UserSerializer(data=user_data)
        if not user_serializer.is_valid():
            print("UserSerializer errors:")
            print(user_serializer.errors)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = user_serializer.save()
        print("User created successfully:")
        print(user)

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
                print("Image successfully decoded and converted to file.")
            except Exception as e:
                print("Error decoding base64 image:")
                print(str(e))
                return Response({'error': 'Invalid image format'}, status=status.HTTP_400_BAD_REQUEST)

        print("Final student_data to be validated:")
        print(student_data)

        # Validate and save the student data
        student_serializer = StudentSerializer(data=student_data, context={'request': request})
        if not student_serializer.is_valid():
            print("StudentSerializer errors:")
            print(student_serializer.errors)
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student = student_serializer.save()
        print("Student created successfully:")
        print(student)

        # Combine the response data
        response_data = {
            'user': user_serializer.data,
            'student': student_serializer.data
        }

        print("All data saved. Sending final response.")
        return Response(response_data, status=status.HTTP_201_CREATED)

    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
            'iat': datetime.now(timezone.utc)
        }
        print("payload", payload)
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
        response.data = {
            'username': user.username,
            'user_id': user.id,
            'jwt': token
        }
        return response
    
class UserView(APIView):
    def get(self, request):
        print("Received GET request to /api/user")

        token = request.COOKIES.get('jwt')
        print(f"JWT token from cookies: {token}")

        if not token:
            print("No JWT token found in cookies. Raising AuthenticationFailed.")
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            print(f"Decoded JWT payload: {payload}")
        except jwt.ExpiredSignatureError:
            print("JWT token has expired. Raising AuthenticationFailed.")
            raise AuthenticationFailed('Unauthenticated')
        except jwt.InvalidTokenError as e:
            print(f"Invalid JWT token. Error: {e}")
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id=payload['id']).first()
        if user:
            print(f"User found: {user}")
        else:
            print("No user found with ID from JWT payload. Raising AuthenticationFailed.")
            raise AuthenticationFailed('Unauthenticated')

        serializer = UserSerializer(user)
        print(f"Serialized user data: {serializer.data}")

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



def prepare_image(image):
    """Optimized image preprocessing"""
    try:
        image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image_rgb
    except Exception as e:
        print(f"DEBUG: Error in prepare_image: {str(e)}")
        raise

def verify_faces(ref_img, uploaded_img, tolerance=0.6):
    """Face verification using face_recognition"""
    print("DEBUG: Starting verify_faces")
    try:
        # Get face encodings
        print("DEBUG: Computing face encodings for reference image")
        ref_encodings = face_recognition.face_encodings(ref_img)
        print(f"DEBUG: Reference encodings found: {len(ref_encodings)}")
        
        print("DEBUG: Computing face encodings for uploaded image")
        uploaded_encodings = face_recognition.face_encodings(uploaded_img)
        print(f"DEBUG: Uploaded encodings found: {len(uploaded_encodings)}")
        
        if not ref_encodings or not uploaded_encodings:
            print("DEBUG: No face encodings found in one or both images")
            return False
            
        # Compare faces
        print("DEBUG: Comparing faces")
        results = face_recognition.compare_faces(
            [ref_encodings[0]], 
            uploaded_encodings[0], 
            tolerance=tolerance
        )
        print(f"DEBUG: Face comparison result: {results[0]}")
        return results[0]
    except Exception as e:
        print(f"DEBUG: Error in verify_faces: {str(e)}")
        return False

@method_decorator(csrf_exempt, name='dispatch')
class FaceVerification(View):
    def post(self, request):
        print("DEBUG: Running updated FaceVerification view")
        try:
            # Parse JSON data
            print("DEBUG: Parsing JSON data")
            data = json.loads(request.body)
            student_id = data.get('student_id')
            image_data = data.get('image_data')
            print(f"DEBUG: student_id: {student_id}, image_data present: {bool(image_data)}")

            if not student_id or not image_data:
                print("DEBUG: Missing student_id or image_data")
                return JsonResponse({'error': 'Missing student_id or image_data'}, status=400)

            # Get student
            print(f"DEBUG: Fetching student with user_id: {student_id}")
            try:
                student = Student.objects.get(user_id=student_id)
                print(f"DEBUG: Student found: {student}")
            except Student.DoesNotExist:
                print(f"DEBUG: Student with user_id {student_id} not found")
                return JsonResponse({'error': 'Student not found'}, status=404)

            # Process images
            print("DEBUG: Processing images")
            try:
                # Decode uploaded image
                print("DEBUG: Decoding uploaded image")
                nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
                uploaded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if uploaded is None:
                    print("DEBUG: Failed to decode uploaded image")
                    return JsonResponse({'error': 'Invalid image data'}, status=400)
                print(f"DEBUG: Uploaded image decoded, shape: {uploaded.shape}")
                
                processed_upload = prepare_image(uploaded)
                print("DEBUG: Uploaded image processed")

                # Load and process reference image
                print(f"DEBUG: Loading reference image from {student.student_img.path}")
                ref_img = cv2.imread(student.student_img.path)
                if ref_img is None:
                    print("DEBUG: Failed to load reference image")
                    return JsonResponse({'error': 'Failed to load reference image'}, status=400)
                print(f"DEBUG: Reference image loaded, shape: {ref_img.shape}")
                
                processed_ref = prepare_image(ref_img)
                print("DEBUG: Reference image processed")
            except Exception as e:
                print(f"DEBUG: Image processing error: {str(e)}")
                return JsonResponse({'error': f'Image processing error: {str(e)}'}, status=400)

            # Verify faces
            print("DEBUG: Verifying faces")
            verified = verify_faces(processed_ref, processed_upload)
            print(f"DEBUG: Face verification result: {verified}, type: {type(verified)}")

            # Record attendance
            status = Attendance.PRESENT if verified else Attendance.ABSENT
            print(f"DEBUG: Attendance status: {status}, type: {type(status)}")
            if verified:
                print("DEBUG: Creating attendance record")
                Attendance.objects.create(
                    student=student,
                    status=status,
                    date_time=timezone.now()
                )
                print("DEBUG: Attendance record created")

            # Convert status to a JSON-serializable string
            status_str = status  # Already a string ('Present' or 'Absent')
            print(f"DEBUG: Serialized status: {status_str}, type: {type(status_str)}")

            # Build response
            response_data = {
                'verified': bool(verified),  # Ensure verified is a standard bool
                'status': status_str
            }
            print(f"DEBUG: Response data: {response_data}, types: verified={type(verified)}, status={type(status_str)}")
            return JsonResponse(response_data)

        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"DEBUG: Server error in FaceVerification: {str(e)}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
        
