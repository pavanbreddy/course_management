from django.contrib import admin
from .models import Student, Faculty, Parent, Course, Calender, Parenting, Takes, Teaches

admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Parent)
admin.site.register(Course)
admin.site.register(Calender)
admin.site.register(Parenting)
admin.site.register(Takes)
admin.site.register(Teaches)

# Register your models here.
