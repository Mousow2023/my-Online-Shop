from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from store.models import Product
from .models import Order, Payment, OrderProduct
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.contrib import messages
import datetime
import json

from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url="login")
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body["orderID"])

    # Store transaction details inside payment model
    payment = Payment.objects.create(
        user = request.user,
        payment_id = body["transactionID"],
        payment_method = body["paymentMethod"],
        amount_paid = order.order_total,
        status = body["status"],
    )

    # Update the order model
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move cart items to OrderProduct Model
    cart_items  = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.is_ordered = True
        order_product.save()

        # Get the variations of the ordered product
        cart_item = CartItem.objects.get(id=item.id)
        product_variations = cart_item.variations.all()
        ordered_product = OrderProduct.objects.get(id=order_product.id)
        ordered_product.variation.set(product_variations)
        ordered_product.save()

        # Decrease stock of the sold products
        product = Product.objects.get(id=item.product_id)
        if product.stock >= item.quantity:
            product.stock -= item.quantity
            product.save()
        else:
            messages.error(request, "The stock you're triying to purchase is not available")
        
    # Clear Cart
    CartItem.objects.filter(user=request.user).delete()
    
    # Send order received email to consumer
    email_subject = "Merci de Votre confiance"
    message = render_to_string("orders/order_received_email.html", {
        "user": request.user,
        "order": order,        
    })
    to_email = request.user.email
    send_email = EmailMessage(email_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        "order_number": order.order_number,
        "transactionID": payment.payment_id,
    }

    return JsonResponse(data)


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


def order_successful(request):
    order_number = request.GET.get("order_number")
    transactionID = request.GET.get("payment_id")

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        products_ordered = OrderProduct.objects.filter(order_id=order.id)

        sub_total = 0
        for ordered in products_ordered:
            sub_total += (ordered.product.price * ordered.quantity)

        payment = Payment.objects.get(payment_id=transactionID)

        context = {
            "order": order,
            "products_ordered": products_ordered,
            "transactionID": transactionID,
            "payment": payment,
            "order_number": order.order_number,
            "sub_total": sub_total,
        }
        return render(request, "orders/order_successful.html", context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect("home")