from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by("-created_date")

    # Get the review
    for product in products:
      reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
      "products": products,
      "reviews": reviews,
    }

    return render(request, "home.html", context)


def custom_404_view(request, exception):
	return render(request, "404.html", status=404)


def custom_500_view(request):
    return render(request, "500.html", status=500)
