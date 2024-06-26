from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, ProfileForm
from .models import Account, UserProfile
from orders.models import Order
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
import requests

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

                    for var in product_variation_list:
                        if var in existing_variations_list:
                            index = existing_variations_list.index(var)
                            item_id = cart_item_id_list[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            for var in product_variation_list:
                                if var not in existing_variations_list:
                                    cart_item = CartItem.objects.filter(cart=cart, variations__in=var)
                                    for item in cart_item:
                                        item.user = user
                                        item.save() 
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    next_page = params["next"]
                    return redirect(next_page)
            except:
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
    orders = Order.objects.filter(user_id=request.user.id, is_ordered=True).order_by("-created_at")
    orders_count = orders.count()

    context = {
        "orders_count": orders_count,
    }
    return render(request, "account/dashboard.html", context)


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


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by("-created_at")

    context = {
        "orders": orders,
    }
    return render(request, "account/my_orders.html", context)


@login_required(login_url="login")
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=userprofile)
    
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    }
    return render(request, "account/edit_profile.html", context)


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Account.objects.get(username__iexact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password updated successfully !")
                return redirect("change_password")
            else:
                messages.error(request, "Invalid password")
                return redirect("change_password")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("change_password")
        
    return render(request, "account/change_password.html")
