from django.http import HttpRequest
from django.shortcuts import render
from app.forms import *
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth import login

# Create your views here.

def register(request):
    EUFO = UserForm()
    EPFO = ProfileForm()
    d = {'EUFO': EUFO, 'EPFO':EPFO}
    if request.method == 'POST' and request.FILES:
        UFDO = UserForm(request.POST)
        PFDO = ProfileForm(request.POST, request.FILES)
        if UFDO.is_valid() and PFDO.is_valid():
            pw = UFDO.cleaned_data.get('password')
            MUFDO = UFDO.save(commit=False)
            MUFDO.set_password(pw)
            MUFDO.save()
            MPFDO = PFDO.save(commit=False)
            MPFDO.username=MUFDO
            MPFDO.save()
            message = f"Hello {UFDO.cleaned_data.get('first_name')} Your Registration agaainst our application is Successfull \n \n Thanks & Regards Team"
            email = UFDO.cleaned_data.get('email')
            send_mail(
                'Registration Successfull',
                message,
                'likith.qsp@gmail.com',
                [email],
                fail_silently=False

            )
            return HttpResponse('registration is Done')
        return HttpResponse('Invalid Data')
    return render(request, 'register.html', d)



def user_login(request: HttpRequest) -> HttpResponse:
    """
    Authenticate a user based on username and password.
    
    If successful, log them into the system and redirect to the home page.
    If authentication fails, return an error message.
    """
    if request.method == 'POST':
        username = request.POST.get('un')
        password = request.POST.get('pw')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = username
            return render(request, 'home.html', {'user': user})
        else:
            return HttpResponse('Invalid Credentials')
    return render(request, 'user_login.html')

def user_profile(request):
    try:
        un = request.session['username']
        UO = User.objects.get(username=un)
        d = {'UO':UO}
        request.session.modified = True
        return render(request, 'user_profile.html', d)
    except:
        return render(request, 'user_login.html')    


def home(request):
    request.session.modified = True
    return render(request, 'home.html')

