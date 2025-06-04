from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from api.models import User, Role, Admin, Class, Student, Attendance

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

# Role Serializer
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

# Admin Serializer
class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    role = RoleSerializer()

    class Meta:
        model = Admin
        fields = ['user', 'role', 'first_name', 'last_name']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        role_data = validated_data.pop('role')
        user = User.objects.create(**user_data)
        role, created = Role.objects.get_or_create(name=role_data['name'])
        admin = Admin.objects.create(user=user, role=role, **validated_data)
        return admin

# Class Serializer

# Class Serializer
class ClassSerializer(serializers.ModelSerializer):
    admin = AdminSerializer(read_only=True)

    class Meta:
        model = Class
        fields = ["class_id", "name", "section", "semester", "year", "admin"]


# Student Serializer
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    student_class = ClassSerializer(read_only=True)
    student_img = serializers.ImageField()

    class Meta:
        model = Student
        fields = ["user", "first_name", "middle_name", "last_name", "student_class", "student_img"]


# Attendance Serializer
class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "student", "status", "date_time"]