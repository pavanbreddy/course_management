import re
from django import forms
import datetime
from .models import Student, Parent, Faculty, Course, Calender, Takes, Teaches, Parenting
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import widgets
from django.forms.extras.widgets import SelectDateWidget


student = 0
faculty = 1
PREFERRED_DRINK_CHOICES = (
    (student, 'Student'),
    (faculty, 'Faculty'),
)

class MySelectDateWidget(SelectDateWidget):

    def create_select(self, *args, **kwargs):
        old_state = self.is_required
        self.is_required = False
        result = super(MySelectDateWidget, self).create_select(*args, **kwargs)
        self.is_required = old_state
        return result


class RegistrationForm(forms.Form):
    CHOICES=[('Student','Student'),('Faculty','Faculty')]
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Username"), error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
    firstname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("First Name"))
    lastname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Last Name"))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password (again)"))
    type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(),initial='Student')
    """
        class Meta:
		model=Student
		fields=('name','gender','dob','email')
        """
    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("The username already exists. Please try another one."))


    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return self.cleaned_data



class ProfileForm(forms.ModelForm):
    firstname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("First Name"))
    lastname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Last Name"))
    role = forms.ChoiceField(choices=PREFERRED_DRINK_CHOICES, widget=forms.RadioSelect(),label=_("Role"))


class CourseForm(forms.ModelForm):
    syllabus = forms.CharField(widget=forms.Textarea)
    class Meta:
        model=Course
        fields=('name','instructor','syllabus','prerequisite')




class CourseRegisterForm(forms.ModelForm):
    class Meta:
        model=Takes
        fields=('cid','sid')


class CalenderForm(forms.ModelForm):
    deadline = forms.DateField(label="Scheduled date",required=False,widget=MySelectDateWidget(empty_label=("Choose Year", "Choose Month", "Choose Day"),),)
    docfile = forms.FileField(label='Select a file', help_text='max. 42 megabytes')
    event = forms.CharField(widget=forms.Textarea)
    class Meta:
        model=Calender
        fields=('cid','event','deadline','docfile')


class ContactForm(forms.Form):
        subject = forms.CharField(required=True)
        message = forms.CharField(widget=forms.Textarea)
        
        
class ParentForm(forms.Form):
    childid = forms.CharField(required=True)
    emailid = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)))
    #dob = forms.DateField(required=True,widget=MySelectDateWidget(empty_label=("Choose Year", "Choose Month", "Choose Day"),),)             
