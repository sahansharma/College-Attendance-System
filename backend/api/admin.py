from django.contrib import admin

# Register your models here.
from .models import Student, Attendance, User, Class  # Import your models here

# Register your models here
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(User)
admin.site.register(Class)