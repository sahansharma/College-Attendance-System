"""
Django REST Framework Serializers for the Admin Application.

This module provides serializers for admin operations with proper type hints,
validation, and comprehensive error handling following professional
coding practices.
"""

from typing import Dict, Any, TypeVar, Type
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from api.models import User, Role, Admin, Class, Student, Attendance
from .models import AdminUser

# Type variables for generic serialization
T = TypeVar('T')


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
        """
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """
        Update an existing user with proper password handling.
        
        Args:
            instance: The existing User instance to update.
            validated_data: Validated data dictionary.
            
        Returns:
            The updated User instance.
        """
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        
        return super().update(instance, validated_data)


class AdminUserSerializer(serializers.ModelSerializer[AdminUser]):
    """
    Serializer for the AdminUser model with password handling.
    
    Handles admin user creation with proper password hashing.
    """
    
    class Meta:
        """
        Metadata for AdminUserSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
            extra_kwargs: Additional field options (password write-only)
        """
        model: Type[AdminUser] = AdminUser
        fields: list[str] = ['id', 'name', 'username', 'password']
        extra_kwargs: Dict[str, Dict[str, bool]] = {'password': {'write_only': True}}

    def create(self, validated_data: Dict[str, Any]) -> AdminUser:
        """
        Create a new admin user with properly hashed password.
        
        Args:
            validated_data: Validated data dictionary containing user information.
            
        Returns:
            The created AdminUser instance with hashed password.
        """
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance: AdminUser, validated_data: Dict[str, Any]) -> AdminUser:
        """
        Update an existing admin user with proper password handling.
        
        Args:
            instance: The existing AdminUser instance to update.
            validated_data: Validated data dictionary.
            
        Returns:
            The updated AdminUser instance.
        """
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        
        return super().update(instance, validated_data)


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
        """
        user_data: Dict[str, Any] = validated_data.pop('user')
        role_data: Dict[str, Any] = validated_data.pop('role')
        
        user: User = User.objects.create(**user_data)
        
        role_name: str = role_data.get('name', 'Admin')
        role: Role
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
    
    admin: AdminSerializer = AdminSerializer(read_only=True)

    class Meta:
        """
        Metadata for ClassSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
        """
        model: Type[Class] = Class
        fields: list[str] = ["class_id", "name", "section", "semester", "year", "admin"]

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

    def validate_section(self, value: str) -> str:
        """
        Validate class section.
        
        Args:
            value: The section to validate.
            
        Returns:
            The validated section.
        """
        return value.strip() if value else ''


class StudentSerializer(serializers.ModelSerializer[Student]):
    """
    Serializer for the Student model with nested User and Class serializers.
    
    Handles student information serialization with comprehensive validation.
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
        fields: list[str] = ["user", "first_name", "middle_name", "last_name", "student_class", "student_img"]

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
    
    student: StudentSerializer = StudentSerializer(read_only=True)

    class Meta:
        """
        Metadata for AttendanceSerializer.
        
        Attributes:
            model: The Django model to serialize
            fields: Fields to include in the serialization
        """
        model: Type[Attendance] = Attendance
        fields: list[str] = ["id", "student", "status", "date_time"]

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

    def to_representation(self, instance: Attendance) -> Dict[str, Any]:
        """
        Customize the representation of attendance records.
        
        Args:
            instance: The Attendance instance to serialize.
            
        Returns:
            Dictionary representation of the attendance record.
        """
        representation: Dict[str, Any] = super().to_representation(instance)
        
        if instance.student:
            representation['student_name'] = (
                f"{instance.student.first_name} "
                f"{instance.student.middle_name or ''} "
                f"{instance.student.last_name}"
            ).strip()
            
        return representation
