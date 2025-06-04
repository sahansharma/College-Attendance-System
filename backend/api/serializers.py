from rest_framework import serializers
from .models import User, Student, Class

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['class_id', 'name', 'section', 'semester', 'year']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print("I am inside user serializer",validated_data)
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user

class StudentSerializer(serializers.ModelSerializer):
    student_class = ClassSerializer()

    class Meta:
        model = Student
        fields = ['user', 'first_name', 'middle_name', 'last_name', 'student_class', 'student_img']

    def create(self, validated_data):
        student_class_data = validated_data.pop('student_class')
        student_class, created = Class.objects.get_or_create(
            name=student_class_data['name'],
            section=student_class_data['section'],
            semester=student_class_data['semester'],
            year=student_class_data['year']
        )
        user = validated_data.pop('user')
        student = Student.objects.create(
            user=user,
            first_name=validated_data['first_name'],
            middle_name=validated_data['middle_name'],
            last_name=validated_data['last_name'],
            student_class=student_class,
            student_img=validated_data.get('student_img')  # Handle optional student_img
        )
        return student

