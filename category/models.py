from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    category_image = models.ImageField(upload_to="photos/categories", blank=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "catogories"
        
    # def get_absolute_url(self):
    #     return reverse("product_by_category", kwargs={"category_slugs": self.slug})
    


    def __str__(self):
        return self.category_name