from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.http import HttpResponse
from carts.models import Cart, CartItem
from carts.views import _get_cart_id

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
            try:
                cart = Cart.objects.get(cart_id=_get_cart_id(request))
                is_cart_item = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Get the product variations by cart id
                    product_variation_list = []
                    for item in cart_item:
                        product_variation_list.append(list(item.variations.all()))


                    # Get the existing variations of the cart items of the user
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variations_list = []
                    cart_item_id_list = []
                    for item in cart_item:
                        existing_variations_list.append(list(item.variations.all()))
                        cart_item_id_list.append(item.id)
                        
                    for variation in product_variation_list:
                        index = existing_variations_list.index(variation)
                        item_id = cart_item_id_list[index]
                        item = CartItem.objects.get(id=item_id)
                        item.quantity += 1
                        item.user = user
                        item.save()
                    else:
                        cart_item = CartItem.objects.create(cart=cart)
                        for item in cart_item:
                            item.user = user
                            item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")
    return render(request, "account/login.html")


@login_required(login_url="login")
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


@login_required(login_url="login")
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
    

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("reset_password")
    else:
        messages.error(request, "Invalid reset password path")
        return redirect("login")
    

def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password has been reset successfully!")
            return redirect("login")
        else:
            messages.error(request, "Password and confirmation do not match")
            return redirect("reset_password")
    else:
        return render(request, "account/reset_password.html")




