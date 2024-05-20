from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required

# Create your views here.
def _get_cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, product_id):
    # Get the product
    product = Product.objects.get(id=product_id)
    current_user = request.user
    # If the user is authenticated
    if current_user.is_authenticated:
        # Get the product variations
        product_variations = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variations.append(variation)
                except:
                    pass

        # Get the cart item
        is_cart_item = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            # Get the existing variations of the cart_item
            existing_variations_list = []
            cart_item_id_list = []
            for item in cart_item:
                existing_variations_list.append(list(item.variations.all()))
                cart_item_id_list.append(item.id)

            # Check if the product variations are in the cart item
            if product_variations in existing_variations_list:
                # Update the quantity of the cart item
                    # Get the id of the cart_item  
                index = existing_variations_list.index(product_variations)
                item = CartItem.objects.get(product=product, id=cart_item_id_list[index])
                item.quantity += 1
                item.save()
            else:
                # Create a new cart item
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variations) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variations)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)
            cart_item.save()

        return redirect("cart")
    # if the user is not authenticated
    else:
        # Get the product variations
        product_variations = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variations.append(variation)
                except:
                    pass
        
        # Get the cart
        try:
            user_cart = Cart.objects.get(cart_id=_get_cart_id(request))  # Rename the variable
        except Cart.DoesNotExist:
            user_cart = Cart.objects.create(
                cart_id=_get_cart_id(request)
            )
        user_cart.save()

        # Get the cart item
        is_cart_item = CartItem.objects.filter(product=product, cart=user_cart).exists()
        if is_cart_item:
            cart_item = CartItem.objects.filter(product=product, cart=user_cart)

            # Get the existing variations of the cart_item
            existing_variations_list = []
            cart_item_id_list = []
            for item in cart_item:
                existing_variations_list.append(list(item.variations.all()))
                cart_item_id_list.append(item.id)

            # Check if the product variations are in the cart item
            if product_variations in existing_variations_list:
                # Update the quantity of the cart item
                    # Get the id of the cart_item  
                index = existing_variations_list.index(product_variations)
                item = CartItem.objects.get(product=product, id=cart_item_id_list[index])
                item.quantity += 1
                item.save()
            else:
                # Create a new cart item
                item = CartItem.objects.create(product=product, quantity=1, cart=user_cart)
                if len(product_variations) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variations)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=user_cart
            )
            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)
            cart_item.save()

        return redirect("cart")


def remove_from_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect("cart")


def delete_from_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        
    cart_item.delete()
    return redirect("cart")


def cart(request, total_price=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            total_price += (item.product.price * item.quantity)
    except ObjectDoesNotExist:
        pass

    tax = (3 * total_price) / 100
    total = tax + total_price

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "quantity": quantity,
        "tax": tax,
        "total": total
    }

    return render(request, "store/cart.html", context)


@login_required(login_url="login")
def checkout(request, total_price=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            total_price += (item.product.price * item.quantity)
    except ObjectDoesNotExist:
        pass

    tax = (3 * total_price) / 100
    total = tax + total_price

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "quantity": quantity,
        "tax": tax,
        "total": total
    }
    return render(request, "store/checkout.html", context)

