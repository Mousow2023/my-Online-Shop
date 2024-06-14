from django.shortcuts import render, redirect
from carts.models import Cart, CartItem
from .forms import OrderForm
from .models import Order
import datetime

from django.contrib.auth.decorators import login_required

# Create your views here.

def payments(request):
    return render(request, "orders/payments.html")

@login_required(login_url="login")
def place_order(request, total_price=0, quantity=0):
    current_user = request.user

    # Redirect the user to the store in there is not Cart Item in the Cart
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() < 0:
        return redirect("store_index")
    
    total = 0
    tax = 0
    for cart_item in cart_items:
        total_price += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (3 * total_price) / 100
    total = tax + total_price

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Save the order data in the Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context = {
                "order": order,
                "total_price": total_price,
                "total": total,
                "tax": tax,
                "cart_items": cart_items,
            }

            return render(request, "orders/payments.html", context)
        else:
            # Form is invalid, print errors to debug
            print(form.errors)
  
    return redirect("checkout")

