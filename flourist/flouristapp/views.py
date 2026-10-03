from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

from .models import Home, Men, Women, Kids, Order, Profile, Wishlist
import json
import os
from pathlib import Path

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt

from dotenv import load_dotenv
import google.generativeai as genai

 
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ================= HOME =================
def home(request):
    post = Home.objects.all().order_by('-id')
    return render(request, "home.html", {'post': post})


# ================= CATEGORY PAGES =================
def men(request):
    post = Men.objects.all().order_by('-id')
    return render(request, "men.html", {'post': post})


def women(request):
    post = Women.objects.all().order_by('-id')
    return render(request, "women.html", {'post': post})


def kids(request):
    post = Kids.objects.all().order_by('-id')
    return render(request, "kids.html", {'post': post})

 
  
 # ================= CART =================
def add_to_cart(request, model, id):

    model_map = {
        "home": Home,
        "men": Men,
        "women": Women,
        "kids": Kids,
    }

    ProductModel = model_map.get(model.lower())

    if not ProductModel:
        return redirect("home")

    item = get_object_or_404(ProductModel, id=id)

    cart = request.session.get("cart", [])

    cart.append({
        "model": model,
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "image": item.image.url if item.image else "",
    })

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("my_cart")


def my_cart(request):
    cart = request.session.get("cart", [])
    return render(request, "my_cart.html", {"cart": cart})
# ================= PAYMENT =================
@login_required
def payment(request, id, model_name):

    model_map = {
        "Home": Home,
        "Men": Men,
        "Women": Women,
        "Kids": Kids,
    }

    model = model_map.get(model_name)

    if not model:
        return redirect("home")

    item = get_object_or_404(model, id=id)

    return render(request, "payment.html", {
        "item": item,
        "model_name": model_name,
    })


# ================= SCAN PAYMENT =================
@login_required
def scan_payment(request, model_name, id):

    print("SCAN PAYMENT OPENED")
    print("MODEL:", model_name)
    print("ID:", id)
    print("USER:", request.user)

    model_map = {
        "home": Home,
        "men": Men,
        "women": Women,
        "kids": Kids,
    }

    ProductModel = model_map.get(model_name.lower())

    if not ProductModel:
        print("MODEL NOT FOUND")
        return redirect("home")

    item = get_object_or_404(ProductModel, id=id)

    if request.method == "POST":

        print("POST RECEIVED")

        Order.objects.create(
            user=request.user,
            product_name=item.name,
            product_image=item.image,
            price=item.price,
            quantity=1,
            status="Pending"
        )

        print("ORDER CREATED")

        return redirect("success")

    return render(request, "scan.html", {
        "item": item,
        "model_name": model_name,
    })
   
# ================= PAYMENT WRAPPERS =================

@login_required
def home_payment(request, id):
    return payment(request, id, "Home")


@login_required
def men_payment(request, id):
    return payment(request, id, "Men")


@login_required
def women_payment(request, id):
    return payment(request, id, "Women")


@login_required
def kids_payment(request, id):
    return payment(request, id, "Kids")


# ================= SUCCESS =================
def success(request):
    return render(request, 'success.html')


# ================= SEARCH =================
def search(request):
    query = request.GET.get('q')

    if query:
        if Men.objects.filter(name__icontains=query).exists():
            return redirect('men')
        elif Women.objects.filter(name__icontains=query).exists():
            return redirect('women')
        elif Kids.objects.filter(name__icontains=query).exists():
            return redirect('kids')

    return redirect('home')


# ================= AUTH =================
def login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            auth_login(request, user)
            return redirect('home')

        return render(request, 'login.html', {
            'error': 'Invalid Username or Password'
        })

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists'
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(request, 'register.html')


# ================= PROFILE =================
@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        request.user.first_name = request.POST.get("first_name", "")
        request.user.last_name = request.POST.get("last_name", "")
        request.user.save()

        profile.phone = request.POST.get("phone", "")
        profile.address = request.POST.get("address", "")

        birthday = request.POST.get("birthday")
        profile.birthday = birthday if birthday else None

        profile.save()

    orders = Order.objects.filter(user=request.user).order_by('-order_date')

    return render(request, "profile.html", {
        "profile": profile,
        "orders": orders
    })


# ================= ORDERS =================
@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders.html', {'orders': orders})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, "my_orders.html", {"orders": orders})


# ================= CREATE ORDER =================
@login_required
def create_order(request, product_id):

    product = get_object_or_404(Men, id=product_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        Order.objects.create(
            user=request.user,
            product_name=product.name,
            product_image=product.image,
            price=product.price,
            quantity=quantity
        )

        return redirect("success")

    return render(request, "checkout.html", {"product": product})


# ================= WISHLIST =================
@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).order_by('-id')
    return render(request, "wishlist.html", {"items": items})


@login_required
def add_to_wishlist(request, id, model):

    model_map = {
        "Men": Men,
        "Women": Women,
        "Kids": Kids,
        "Home": Home,
    }

    ProductModel = model_map.get(model)

    if not ProductModel:
        return redirect('wishlist')

    item = get_object_or_404(ProductModel, id=id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product_name=item.name,
        product_image=item.image,
        
    )

    return redirect('wishlist')


@login_required
def remove_wishlist(request, id):
    item = get_object_or_404(Wishlist, id=id, user=request.user)
    item.delete()
    return redirect('wishlist')

# ================= TRACKING =================
@login_required
def tracking(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'tracking.html', {'orders': orders})


# ================= AI================= 
@csrf_exempt
def ai_chat(request):

    if request.method == "POST":

        try:

            data = json.loads(request.body)
            message = data.get("message", "").lower().strip()

            products = []

            # ---------------- HOME ----------------
            for item in Home.objects.all():

                products.append({
                    "id": item.id,
                    "category": "Home",
                    "name": item.name,
                    "price": item.price,
                    "image": item.image.url
                })

            # ---------------- MEN ----------------
            for item in Men.objects.all():

                products.append({
                    "id": item.id,
                    "category": "Men",
                    "name": item.name,
                    "price": item.price,
                    "image": item.image.url
                })

            # ---------------- WOMEN ----------------
            for item in Women.objects.all():

                products.append({
                    "id": item.id,
                    "category": "Women",
                    "name": item.name,
                    "price": item.price,
                    "image": item.image.url
                })

            # ---------------- KIDS ----------------
            for item in Kids.objects.all():

                products.append({
                    "id": item.id,
                    "category": "Kids",
                    "name": item.name,
                    "price": item.price,
                    "image": item.image.url
                })

            # ---------------- FIND MATCHING PRODUCTS ----------------

            matched_products = []

            words = message.split()

            for product in products:

                product_name = product["name"].lower()
                category = product["category"].lower()

                if any(word in product_name for word in words) or any(word in category for word in words):

                    matched_products.append(product)

            # No matching products
            if len(matched_products) == 0:

                return JsonResponse({
                    "reply": "Sorry, I couldn't find any matching products.",
                    "products": []
                })

            # ---------------- GEMINI PROMPT ----------------

            available_products = ""

            for product in matched_products:

                available_products += (
                    f'{product["category"]} | '
                    f'{product["name"]} | '
                    f'₹{product["price"]}\n'
                )

            prompt = f"""
You are an AI Shopping Assistant.

Available Products:

{available_products}

Customer Question:
{message}

Rules:

1. Recommend ONLY the products listed above.
2. Mention the product name and price.
3. Do not invent products.
4. Keep the answer short and friendly.
"""

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)

            return JsonResponse({
                "reply": response.text,
                "products": matched_products
            })

        except Exception as e:

            return JsonResponse({
                "reply": str(e),
                "products": []
            })

    return JsonResponse({
        "reply": "Only POST request allowed",
        "products": []
    })
# ================= LOGOUT =================
def user_logout(request):
    logout(request)
    return redirect('home')


 