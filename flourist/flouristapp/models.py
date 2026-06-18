from django.db import models
from django.contrib.auth.models import User


# ---------- HOME ----------
class Home(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='home/')
    price = models.IntegerField()

    def __str__(self):
        return self.name


# ---------- MEN ----------
class Men(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='men/')
    price = models.IntegerField()

    def __str__(self):
        return self.name


# ---------- WOMEN ----------
class Women(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='women/')
    price = models.IntegerField()

    def __str__(self):
        return self.name


# ---------- KIDS ----------
class Kids(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='kids/')
    price = models.IntegerField()

    def __str__(self):
        return self.name


# ---------- PROFILE ----------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    phone = models.CharField(max_length=15, null=True, blank=True) 
    address = models.TextField(blank=True)
    birthday = models.DateField(null=True, blank=True) 


# ---------- ORDER ----------
class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # store product details directly
    product_name = models.CharField(max_length=255)
    product_image = models.ImageField(upload_to='orders/', blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date']

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.product_name}"
# ---------- WISHLIST ----------
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_image = models.ImageField(upload_to='wishlist/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name
        

        