"""
Django REST Framework Serializers for the College Attendance System.

This module provides serializers for all models with proper type hints,
validation, and comprehensive error handling following professional
coding practices.
"""

from typing import Dict, Any, TypeVar, Type
from rest_framework import serializers
from .models import User, Role, Admin, Student, Class, Attendance

# Type variables for generic serialization
T = TypeVar('T')


class RoleSerializer(serializers.ModelSerializer[Role]):
    """
    Serializer for the Role model.
    
    Provides serialization and deserialization for role entries
    with proper type hints and validation.
    """
    
    class Meta:
        """
        Metadata for RoleSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
        """
        model: Type[Role] = Role
        fields: list[str] = ['id', 'name']


class UserSerializer(serializers.ModelSerializer[User]):
    """
    Serializer for the User model with password handling.
    
    Handles user creation with proper password hashing and
    comprehensive validation.
    """
    
    class Meta:
        """
        Metadata for UserSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
            extra_kwargs: Additional field options (password write-only)
        """
        model: Type[User] = User
        fields: list[str] = ['id', 'name', 'username', 'password']
        extra_kwargs: Dict[str, Dict[str, bool]] = {'password': {'write_only': True}}

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create a new user with properly hashed password.
        
        Args:
            validated_data: Validated data dictionary containing user information.
            
        Returns:
            The created User instance with hashed password.
            
        Raises:
            ValueError: If password validation fails.
        """
        password: str | None = validated_data.pop('password', None)
        
        if password is None:
            raise ValueError("Password is required for user creation")
        
        user: User = User.objects.create(**validated_data)
        
        if password is not None:
            user.set_password(password)
            user.save()
            
        return user

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """
        Update an existing user with proper password handling.
        
        Args:
            instance: The existing User instance to update.
            validated_data: Validated data dictionary.
            
        Returns:
            The updated User instance.
        """
        password: str | None = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password is not None:
            instance.set_password(password)
            
        instance.save()
        return instance


class AdminSerializer(serializers.ModelSerializer[Admin]):
    """
    Serializer for the Admin model with nested User and Role serializers.
    
    Handles admin creation with proper user and role handling.
    """
    
    user: UserSerializer = UserSerializer()
    role: RoleSerializer = RoleSerializer()

    class Meta:
        """
        Metadata for AdminSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
        """
        model: Type[Admin] = Admin
        fields: list[str] = ['user', 'role', 'first_name', 'last_name']

    def create(self, validated_data: Dict[str, Any]) -> Admin:
        """
        Create a new admin with nested user and role.
        
        Args:
            validated_data: Validated data containing admin, user, and role info.
            
        Returns:
            The created Admin instance.
            
        Raises:
            ValueError: If required nested data is missing.
        """
        user_data: Dict[str, Any] = validated_data.pop('user')
        role_data: Dict[str, Any] = validated_data.pop('role')
        
        if not user_data:
            raise ValueError("User data is required for admin creation")
        
        user: User = User.objects.create(**user_data)
        
        role_name: str = role_data.get('name', 'Admin')
        role: Role
        _created: bool
        role, _created = Role.objects.get_or_create(name=role_name)
        
        admin: Admin = Admin.objects.create(
            user=user,
            role=role,
            **validated_data
        )
        
        return admin


class ClassSerializer(serializers.ModelSerializer[Class]):
    """
    Serializer for the Class model.
    
    Handles class/lecture group serialization and validation.
    """
    
    class Meta:
        """
        Metadata for ClassSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
        """
        model: Type[Class] = Class
        fields: list[str] = ['class_id', 'name', 'section', 'semester', 'year']

    def validate_name(self, value: str) -> str:
        """
        Validate class name is not empty.
        
        Args:
            value: The class name to validate.
            
        Returns:
            The validated class name.
            
        Raises:
            serializers.ValidationError: If name is empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Class name cannot be empty")
        return value.strip()

    def validate_year(self, value: int) -> int:
        """
        Validate class year is reasonable.
        
        Args:
            value: The year to validate.
            
        Returns:
            The validated year.
            
        Raises:
            serializers.ValidationError: If year is invalid.
        """
        if value < 2000 or value > 2100:
            raise serializers.ValidationError("Year must be between 2000 and 2100")
        return value


class StudentSerializer(serializers.ModelSerializer[Student]):
    """
    Serializer for the Student model with nested User and Class serializers.
    
    Handles student registration with image upload support.
    """
    
    user: UserSerializer = UserSerializer(read_only=True)
    student_class: ClassSerializer = ClassSerializer(read_only=True)
    student_img: serializers.ImageField = serializers.ImageField(required=False)

    class Meta:
        """
        Metadata for StudentSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
        """
        model: Type[Student] = Student
        fields: list[str] = [
            'user', 'first_name', 'middle_name', 'last_name', 
            'student_class', 'student_img'
        ]

    def create(self, validated_data: Dict[str, Any]) -> Student:
        """
        Create a new student with nested user and class relationships.
        
        Args:
            validated_data: Validated data containing student, user, and class info.
            
        Returns:
            The created Student instance.
        """
        student_class_data: Dict[str, Any] = validated_data.pop('student_class', {})
        user: User = validated_data.pop('user')
        
        student_class: Class | None = None
        
        if student_class_data:
            student_class, _created = Class.objects.get_or_create(
                name=student_class_data.get('name', ''),
                section=student_class_data.get('section', ''),
                semester=student_class_data.get('semester', 1),
                year=student_class_data.get('year', 2024),
                defaults={
                    'name': student_class_data.get('name', ''),
                    'section': student_class_data.get('section', ''),
                    'semester': student_class_data.get('semester', 1),
                    'year': student_class_data.get('year', 2024),
                }
            )
        
        student: Student = Student.objects.create(
            user=user,
            first_name=validated_data.get('first_name', ''),
            middle_name=validated_data.get('middle_name', ''),
            last_name=validated_data.get('last_name', ''),
            student_class=student_class,
            student_img=validated_data.get('student_img')
        )
        
        return student

    def validate_first_name(self, value: str) -> str:
        """
        Validate first name is not empty.
        
        Args:
            value: The first name to validate.
            
        Returns:
            The validated first name.
            
        Raises:
            serializers.ValidationError: If first name is empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("First name cannot be empty")
        return value.strip()

    def validate_last_name(self, value: str) -> str:
        """
        Validate last name is not empty.
        
        Args:
            value: The last name to validate.
            
        Returns:
            The validated last name.
            
        Raises:
            serializers.ValidationError: If last name is empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Last name cannot be empty")
        return value.strip()


class AttendanceSerializer(serializers.ModelSerializer[Attendance]):
    """
    Serializer for the Attendance model with nested Student serializer.
    
    Handles attendance records with comprehensive validation.
    """
    
    student: UserSerializer = UserSerializer(read_only=True)

    class Meta:
        """
        Metadata for AttendanceSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
        """
        model: Type[Attendance] = Attendance
        fields: list[str] = ['id', 'student', 'status', 'date_time']

    def validate_status(self, value: str) -> str:
        """
        Validate attendance status is one of the allowed values.
        
        Args:
            value: The status value to validate.
            
        Returns:
            The validated status.
            
        Raises:
            serializers.ValidationError: If status is invalid.
        """
        valid_statuses: list[str] = [Attendance.PRESENT, Attendance.ABSENT, Attendance.LATE]
        
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value

    def create(self, validated_data: Dict[str, Any]) -> Attendance:
        """
        Create an attendance record with proper student lookup.
        
        Args:
            validated_data: Validated data containing attendance information.
            
        Returns:
            The created Attendance instance.
        """
        student_data: Dict[str, Any] = validated_data.pop('student')
        user_id: int = student_data.get('user', 0)
        
        student: Student = Student.objects.get(user_id=user_id)
        
        attendance: Attendance = Attendance.objects.create(
            student=student,
            **validated_data
        )
        
        return attendance

    def to_representation(self, instance: Attendance) -> Dict[str, Any]:
        """
        Customize the representation of attendance records.
        
        Args:
            instance: The Attendance instance to serialize.
            
        Returns:
            Dictionary representation of the attendance record.
        """
        representation: Dict[str, Any] = super().to_representation(instance)
        
        if instance.student and instance.student.user:
            representation['student_name'] = instance.student.user.name
            
        return representation
