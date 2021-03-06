import datetime
from login.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login,authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.template import RequestContext
from .models import Student, Course,Faculty,Calender, Teaches, Takes
from django.shortcuts import render, get_object_or_404, redirect,render_to_response
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            first_name=form.cleaned_data['firstname'],
            last_name=form.cleaned_data['lastname'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            typ=form.cleaned_data['type']
            if(typ=='Student'):
                user.is_staff=0
            else:
                user.is_staff=1
            user.save()
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
    'form': form
    })

    return render_to_response(
    'registration/register.html',
    variables,
    )

def mylogin(request):

    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            if user.is_staff==True:
                return HttpResponseRedirect('/faculty')
            else:
                return HttpResponseRedirect('/student')

    return render_to_response('registration/login.html',context_instance=RequestContext(request))



def register_success(request):
    return render_to_response(
    'registration/success.html',
    )

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def sthome(request):
    regcourses=Takes.objects.filter(sid=request.user.id)
    #print regcourses[0].cid
    reg_distinct=[]
    for i in range(0,len(regcourses)):
        reg_distinct.append(regcourses[i].cid)
    reg_distinct = set(reg_distinct)
    #print reg_distinct
    course = Calender.objects.filter(cid__in=reg_distinct,deadline__lte=datetime.datetime.today()+datetime.timedelta(days=10)).order_by('deadline')
    #course.append(Calender.objects.filter(cid__in=reg_distinct,deadline__lte=datetime.datetime.today()+datetime.timedelta(days=10)))
    #course=set(course)
    return render_to_response(
    'student.html',
    { 'user': request.user,'course':course }
    )


@login_required
def fhome(request):
    return render_to_response(
    'faculty.html',
    { 'user': request.user }
    )

@csrf_protect
@login_required
def courseadd(request):
    instance = Course(instructor=request.user)
    form1a = CourseForm(instance=instance)
    form1a.fields['instructor'].widget = forms.HiddenInput()

    if request.method == "POST":
        form1a = CourseForm(request.POST)
        if form1a.is_valid():
            #form1a.instructor=request.user
            #form1a.fields['instructor'].widget.attrs['disabled'] = True
            course = form1a.save(commit=False)
            course.save()
            return redirect('/faculty/',pk=course.pk)
    else:
        form1a = CourseForm(instance=instance)
        form1a.fields['instructor'].widget = forms.HiddenInput()
        #form1a.fields['instructor'].widget.attrs['disabled'] = True
    return render(request,'courseadd.html',{'form1': form1a })


@csrf_protect
@login_required
def courseregister(request):
    instance1 = Takes(sid=request.user)
    regcourses=Takes.objects.filter(sid=request.user.id)
    #print instance1
    form2 = CourseRegisterForm(instance=instance1)
    form2.fields['sid'].widget = forms.HiddenInput()
    #cour = Course.objects.all()
    reg_distinct=[]
    for i in range(0,len(regcourses)):
        reg_distinct.append(regcourses[i].cid)
    reg_distinct = set(reg_distinct)
    #print reg_distinct
    #print getattr(instance1,'sid')
    if request.method == "POST":
        form2 = CourseRegisterForm(request.POST)
        user = request.user
        if form2.is_valid():
            #form2.sid=request.user.id
            course = form2.cleaned_data['cid']
            print course.prerequisite
            print regcourses
            if course in reg_distinct:
                flag="c"
                return render(request,'payfees.html',{'course':course,'flag':flag,'reg_distinct':reg_distinct})
            elif course.prerequisite not in reg_distinct and course.prerequisite!=None:
                flag="b"
                return render(request,'payfees.html',{'course':course,'flag':flag,'reg_distinct':reg_distinct})         
            else:
                flag="a"
                print course    
                #return render(request,'payfees.html',{'course':course,'flag':flag,'reg_distinct':reg_distinct,'fees':100,'n':1})    
                from_email=user.username+"@coursemanagement.com"
                admin_email="no-reply@coursemanagement.com"
                reply_email = user.email
                print flag
                email = EmailMessage(str(course.name)+" enroll", "Please enroll me to the course.\n\n"+"Click on the link to enroll "+str(user)+ " http://localhost:8000", from_email, [course.instructor.email], headers = {'Reply-To': reply_email})
                email.send()
                
                email1 = EmailMessage(str(course.name)+" enrollment", " you have enrolled to the course " +course.name+" with the email id "+user.email+".",admin_email,[user.email])
                email1.send() 
                course_reg = form2.save(commit=False)
                course_reg.save()
                #print form2
                return redirect('/payfees/',pk=course_reg.pk,flag="a",n=1,fees=100)
    else:
        form2 = CourseRegisterForm(instance=instance1)
        form2.fields['sid'].widget = forms.HiddenInput()
        #form2.fields['sid'].widget.attrs['disabled'] = True
        return render(request, 'courseregister.html',{'form2':form2})

@csrf_protect
@login_required
def coursedisplay(request):
    courses=Course.objects.all()
    user=request.user
    return render(request, 'coursedisplay.html',{'user':user,'courses':courses})

@csrf_protect
@login_required
def coursedetail(request,pk):
    course = get_object_or_404(Course, pk=pk)
    user=request.user
    events=Calender.objects.filter(cid=pk).order_by('-time')
    if request.method == 'GET':
        form = ContactForm()
    else:
        form=ContactForm(request.POST);
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email=user.username+"@coursemanagement.com"
            reply_email = user.email
            email = EmailMessage(subject, message, from_email, [course.instructor.email], headers = {'Reply-To': reply_email})
            email.send()

    return render(request, 'coursedetail.html', {'course':course,'events':events,'form':form})


@csrf_protect
@login_required
def registeredcourses(request):
    regcourses=Takes.objects.filter(sid=request.user.id)
    user=request.user
    reg_distinct=[]
    for i in range(0,len(regcourses)):
        reg_distinct.append(regcourses[i].cid)
    reg_distinct = set(reg_distinct)
    #print reg_distinct
    createdcourses=Course.objects.filter(instructor=request.user)
    return render_to_response('registeredcourses.html',{'user':user,'regcourses':reg_distinct,'createdcourses':createdcourses})



@csrf_protect
@login_required
def payfees(request):
    #n=len(Takes.objects.filter(sid=request.user.id))
    n=1
    fees=100
    return render_to_response('payfees.html',{'fees':fees,'n':n})

@csrf_protect
@login_required
def feesuccess(request):
    n=len(Takes.objects.filter(sid=request.user.id))
    fees=100
    return render_to_response('feesuccess.html',{'fees':fees})


@csrf_protect
@login_required
def addevent(request,pk):
    course = get_object_or_404(Course, pk=pk)
    instance_eve = Calender(cid=course)
    formcal = CourseRegisterForm(instance=instance_eve)
    formcal.fields['cid'].widget = forms.HiddenInput()

    #courses = Calender.objects.filter(x__contains=cid)
    #print courses
    formcal = CalenderForm()
    if request.method == "POST":
        formcal = CalenderForm(request.POST,request.FILES)
        if formcal.is_valid():
            #newdoc = Calender(docfile = request.FILES['docfile'])
            #newdoc.save()
            course = formcal.save(commit=False)
            course.save()
            return redirect('/faculty/',pk=course.pk)
    else:
        formcal = CalenderForm(instance=instance_eve)
        formcal.fields['cid'].widget = forms.HiddenInput()
        #formcal.fields['cid'].widget = forms.HiddenInput()
    #events=Calender.objects.all()
    return render(request,'addevent.html',{'formcal': formcal,'course':course })


@csrf_protect
def parent(request):
    """if request.method == 'GET':
        form = ParentForm()
        return render(request,'parent.html',{'form': form})  
        """
    
    """
    form = ParentForm()    
    if request.method == 'POST':
        form=ParentForm(request.POST);
        if form.is_valid():
            childid = form.cleaned_data['childid']
            emailid = form.cleaned_data['emailid']    
            user = User.objects.filter(username=childid)
            print user
            if user.email == emailid:  
                regcourses=Takes.objects.filter(sid=user.username)
                reg_distinct=[]
                for i in range(0,len(regcourses)):
                    reg_distinct.append(regcourses[i].cid)
                reg_distinct = set(reg_distinct)
                print reg_distinct
        return render(request,'parent.html',{'user':user,'regcourses':reg_distinct})

    else:
        form=ParentForm();        
    return render(request,'parent.html',{'form': form})   
    """
    
    request_params = request.GET.copy()
    print request_params
    user = User.objects.filter(username=request_params.get('childid')).filter(email = request_params.get('emailid') )
    print user
    reg_distinct=[]
    #if user == request_params.get('emailid',''):
    regcourses=Takes.objects.filter(sid=user)
       
    for i in range(0,len(regcourses)):
        reg_distinct.append(regcourses[i].cid)
    reg_distinct = set(reg_distinct)
    print reg_distinct     
    return render(request,'parent.html',{'user':user,'regcourses':reg_distinct})
           
                
"""
def upcomingevent(request,pk):

    print "Frodo"
"""


                      
    
