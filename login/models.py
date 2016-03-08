from django.db import models
from enumfields import EnumField
from enum import Enum
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


# Create your models here.

class StudentYears(Enum):
    Freshman = 1
    Sophomore = 2
    Junior = 3
    Senior = 4
    
class Gender(Enum):
    Male = 1
    Female = 0
    Other = 2    

class Student(models.Model): 
    #sid = models.AutoField()
    userid = models.ForeignKey(User)
    name = models.CharField(max_length=60)
    gender = EnumField(Gender, max_length=10)
    dob = models.DateField(auto_now=False, auto_now_add=False)
    email = models.EmailField()
    year = EnumField(StudentYears, max_length=15)
    
    def __str__(self):
        return str(self.id)
    
    
class Faculty(models.Model):
    #eid = models.AutoField()
    name = models.CharField(max_length=60)
    gender = EnumField(Gender, max_length=10)
    dob = models.DateField(auto_now=False, auto_now_add=False)
    email = models.EmailField()
    def __str__(self):
        return str(self.id)+"   "+self.name        
    
    
class Parent(models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField()
    contact = PhoneNumberField()
    
    def __str__(self):
        return str(self.id)+"   "+self.name


class Course(models.Model):
    #cid = models.AutoField()
    instructor = models.ForeignKey('auth.User')
    name = models.CharField(max_length=60)
    #instructor = models.ForeignKey('Faculty',on_delete=models.CASCADE)
    syllabus = models.CharField(max_length=1000)
    prerequisite = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True)
    def __str__(self):
        return str(self.id)+"   "+self.name
    
    
class Calender(models.Model):
    cid = models.ForeignKey('Course', on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)
    docfile = models.FileField(upload_to='documents/%Y/%m/%d',null=True)
    deadline = models.DateField(auto_now=False,null=True)
    event = models.CharField(max_length=200)
    def __str__(self):
        return str(self.id)+" "+self.event

        
                    
class Parenting(models.Model):
    sid = models.ForeignKey('Student', on_delete=models.CASCADE)
    pid = models.ForeignKey('Parent', on_delete=models.CASCADE) 
    
    def __str__(self):
        return str(self.pid)+"  is parent of  "+str(self.sid)  
    
    
class Takes(models.Model):
    sid = models.ForeignKey('auth.User')
    cid = models.ForeignKey('Course', on_delete=models.CASCADE)    
  
    def __str__(self):
        return str(self.id)
  
class Teaches(models.Model):
    eid = models.ForeignKey('auth.User')
    cid = models.ForeignKey('Course', on_delete=models.CASCADE)  
     
    def __str__(self):
        return str(self.id)     
        


        
