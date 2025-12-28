from typing import Dict, Any
from rest_framework import serializers
from .models import User, Role, Admin, Student, Class, Attendance

class RoleSerializer(serializers.ModelSerializer[Role]):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data: Dict[str, Any]) -> User:
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user

class AdminSerializer(serializers.ModelSerializer[Admin]):
    user = UserSerializer()
    role = RoleSerializer()

    class Meta:
        model = Admin
        fields = ['user', 'role', 'first_name', 'last_name']

    def create(self, validated_data: Dict[str, Any]) -> Admin:
        user_data = validated_data.pop('user')
        role_data = validated_data.pop('role')
        user = User.objects.create(**user_data)
        role, created = Role.objects.get_or_create(name=role_data['name'])
        admin = Admin.objects.create(user=user, role=role, **validated_data)
        return admin

class ClassSerializer(serializers.ModelSerializer[Class]):
    class Meta:
        model = Class
        fields = ['class_id', 'name', 'section', 'semester', 'year']

class StudentSerializer(serializers.ModelSerializer[Student]):
    user = UserSerializer(read_only=True)
    student_class = ClassSerializer(read_only=True)
    student_img = serializers.ImageField(required=False)

    class Meta:
        model = Student
        fields = ['user', 'first_name', 'middle_name', 'last_name', 'student_class', 'student_img']

    def create(self, validated_data: Dict[str, Any]) -> Student:
        student_class_data = validated_data.pop('student_class', {})
        user = validated_data.pop('user')
        
        student_class = None
        if student_class_data:
            student_class, created = Class.objects.get_or_create(
                name=student_class_data['name'],
                section=student_class_data['section'],
                semester=student_class_data['semester'],
                year=student_class_data['year']
            )
        
        student = Student.objects.create(
            user=user,
            first_name=validated_data['first_name'],
            middle_name=validated_data.get('middle_name', ''),
            last_name=validated_data['last_name'],
            student_class=student_class,
            student_img=validated_data.get('student_img')
        )
        return student

class AttendanceSerializer(serializers.ModelSerializer[Attendance]):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'status', 'date_time']

    def create(self, validated_data: Dict[str, Any]) -> Attendance:
        student_data = validated_data.pop('student')
        student = Student.objects.get(user_id=student_data['user'])
        attendance = Attendance.objects.create(student=student, **validated_data)
        return attendance

