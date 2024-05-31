from .forms import UserForm, ProfileForm
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import render
from app.forms import *
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from random import randint

# Create your views here.

def register(request: HttpRequest) -> HttpResponse:
    """
    Handles user registration by validating form data, saving user information, setting a password, and sending a confirmation email.
    
    Args:
    - request: An HttpRequest object that contains method type, POST data, and potentially files for profile data.
    
    Returns:
    - An HttpResponse indicating whether the registration was successful or if there was invalid data.
    - Renders the registration form page with initialized forms if the request is not POST or if validation fails.
    """
    
    user_form = UserForm()
    profile_form = ProfileForm()
    context = {'user_form': user_form, 'profile_form': profile_form}
    
    if request.method == 'POST' and request.FILES:
        user_form_data = UserForm(request.POST)
        profile_form_data = ProfileForm(request.POST, request.FILES)
        
        if user_form_data.is_valid() and profile_form_data.is_valid():
            password = user_form_data.cleaned_data.get('password')
            new_user = user_form_data.save(commit=False)
            new_user.set_password(password)
            new_user.save()
            
            new_profile = profile_form_data.save(commit=False)
            new_profile.username = new_user
            new_profile.save()
            
            message = f"Hello {user_form_data.cleaned_data.get('first_name')} Your Registration against our application is Successful \n \n Thanks & Regards Team"
            email = user_form_data.cleaned_data.get('email')
            
            send_mail(
                'Registration Successful',
                message,
                'likith.qsp@gmail.com',
                [email],
                fail_silently=False
            )
            
            return HttpResponse('Registration is Done')
        
        return HttpResponse('Invalid Data')
    
    return render(request, 'register.html', context)



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


@login_required
def user_profile(request: HttpRequest) -> render:
    """
    Retrieves and displays the profile of a logged-in user based on their session username.

    Inputs:
    - request: An HttpRequest object that includes session data and potentially other user-specific data.

    Outputs:
    - Renders 'user_profile.html' with user data if the user exists and is logged in.
    - Redirects to 'user_login.html' if the user is not found or another issue occurs.
    """
    try:
        username = request.session.get('username')
        user_object = User.objects.get(username=username)
        data = {'user_object': user_object}
        request.session.modified = True
        return render(request, 'user_profile.html', data)
    except User.DoesNotExist:
        return render(request, 'user_login.html')


def home(request):
    request.session.modified = True
    return render(request, 'home.html')


@login_required
def user_logout(request):
    """ To log out a user, call the `user_logout` function with the request object. user_logout(request)
    This will clear the user's session data and redirect to the home page.
    """
    logout(request)
    return render(request, 'home.html')

@login_required
def changepassword(request):
    """
    Allows authenticated users to change their password by verifying a one-time password (OTP) sent to their registered email.

    Inputs:
    - request: An HttpRequest object that contains method type, POST data including new password (`pw`) and confirmation password (`cpw`), and session data.

    Outputs:
    - If the passwords match and the email is sent successfully, the function returns an HttpResponse that renders the OTP verification page (`otp.html`).
    - If the passwords do not match, it returns an HttpResponse with an error message indicating the mismatch.
    """
    if request.method == 'POST':
        pw = request.POST.get('pw')
        cpw = request.POST.get('cpw')
        
        if pw == cpw:
            otp = randint(100000, 999999)
            request.session['pw'] = pw
            request.session['otp'] = otp
            username = request.session.get('username')
            user = User.objects.get(username=username)
            email = user.email
            
            send_mail(
                "RE:- OTP for changing password",
                f"The OTP to change password is: {otp}",
                'likith.qsp@gmail.com',
                [email],
                fail_silently=False
            )
            
            return render(request, 'otp.html')
        
        return HttpResponse('Password is not matching')
    
    return render(request, 'changepassword.html')

def otp(request):
    """
    Validates a user-provided OTP against a session-stored OTP for password change verification.
    If the OTPs match, it updates the user's password in the database.

    Args:
        request (HttpRequest): An HttpRequest object containing the user's POST data and session data.

    Returns:
        HttpResponse: Indicates whether the password was successfully changed or if there was an OTP mismatch.
    """
    if request.method == 'POST':
        UOTP = request.POST.get('otp')
        GOTP = request.session.get('otp')

        if UOTP == str(GOTP):
            username = request.session.get('username')
            user = User.objects.get(username=username)
            new_password = request.session.get('pw')
            user.set_password(new_password)
            user.save()
            return HttpResponse('Password Changed Successfully')

        return HttpResponse('Invalid OTP')

    return render(request, 'otp.html')


def forgetpassword(request):
    if request.method == 'POST':
        un = request.POST.get('un')
        user_obj = User.objects.get(username = un)
        if user_obj:
            request.session['username'] = un
            otp = randint(100000, 999999)
            request.session['otp'] = otp
            send_mail(
                "RE:- OTP for changing password",
                f"The OTP to change password is: {otp}",
                'likith.qsp@gmail.com',
                [user_obj.email],
                fail_silently=False
            )
            return render(request, 'forgetpasswordotp.html')
    return render(request, 'forgetpassword.html')

def forgetpasswordotp(request):
    if request.method == 'POST':
        UOTP = request.POST.get('otp')
        GOTP = request.session['otp']
        if str(GOTP) == UOTP:
            return render(request, 'updatepassword.html')
        return HttpResponse('Invalid OTP')
    return render(request, 'forgetpasswordotp.html')

def updatepassword(request):
    if request.method == 'POST':
        pw = request.POST.get('pw')
        cpw = request.POST.get('cpw')
        if pw == cpw:
            un = request.session['username']
            UO = User.objects.get(username=un)
            UO.set_password(pw)
            UO.save()
            return render(request, 'user_login.html')
        return HttpResponse('Password doesnot mathcing')