from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm
from .models import UserProfile

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, mobile_number=form.cleaned_data['mobile_number'])
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('adoption:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(f"/accounts/reset-password/{user.pk}/{token}/")
            subject = 'Password Reset Request'
            message = f"Click the link to reset your password: {reset_link}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('accounts:login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    return render(request, 'auth/forgot_password.html')

def reset_password(request, user_id, token):
    try:
        user = User.objects.get(pk=user_id)
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                if password1 == password2:
                    user.set_password(password1)
                    user.save()
                    messages.success(request, 'Password reset successful! Please log in.')
                    return redirect('accounts:login')
                else:
                    messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/reset_password.html')
        else:
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('accounts:forgot_password')
    except User.DoesNotExist:
        messages.error(request, 'Invalid user.')
        return redirect('accounts:forgot_password')

@never_cache
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('adoption:home')