from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.http import HttpResponse

# Email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


from django.contrib.auth.decorators import login_required
# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = email,
                password = password,
            )
            user.phone_number = phone_number
            user.save()

            # User verification
            current_site = get_current_site(request)
            email_subject = "Please verify your email"
            message = render_to_string("account/account_verification_email.html", {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(email_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, "Registration successful")
            return redirect("/account/login/?command=verification&email"+email)
        
    else:
        form = RegistrationForm()
    context = {
        "form": form,
    }
    return render(request, "account/register.html", context)

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")
    return render(request, "account/login.html")


login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You'are logged out")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been successfully activated")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("register")


login_required(login_url="login")
def dashboard(request):
    return render(request, "account/dashboard.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Send reset password email
            current_site = get_current_site(request)
            email_subject = "Please reset your password"
            message = render_to_string("account/reset_password_email.html", {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(email_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, "Please verify your email address to reset your passowrd")
            return redirect("login")
            
        else:
            messages.error(request, "Account does not exist")
            
    return render(request, "account/forgot_password.html")
    

def reset_password(request, uidb64, token):
    return HttpResponse("Reset passowod logic here")