# Generated by Django 5.0.1 on 2024-05-05 19:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("carts", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cartitem",
            old_name="Cart",
            new_name="cart",
        ),
    ]
