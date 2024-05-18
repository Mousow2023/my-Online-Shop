from .views import _get_cart_id
from .models import Cart, CartItem

def counter(request):
    cart_counter = 0
    if "admin" in request.path:
        return {}
    else:
        try:
            # cart = Cart.objects.get(cart_id=_get_cart_id(request))
            # cart_items = CartItem.objects.all().filter(cart=cart)
            cart = Cart.objects.filter(cart_id=_get_cart_id(request))

            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
                
            for item in cart_items:
                cart_counter += item.quantity
        except Cart.DoesNotExist:
            cart_counter = 0

    return dict(cart_counter=cart_counter)