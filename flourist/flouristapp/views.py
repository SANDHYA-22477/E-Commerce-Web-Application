from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

from .models import Home, Men, Women, Kids, Order, Profile, Wishlist


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
        "Home": Home,
        "Men": Men,
        "Women": Women,
        "Kids": Kids,
    }

    ProductModel = model_map.get(model)
    item = get_object_or_404(ProductModel, id=id)

    cart = request.session.get('cart', [])

    cart.append({
        'model': model,
        'id': item.id,
        'name': item.name,
        'price': item.price,
        'image': item.image.url if item.image else '',
    })

    request.session['cart'] = cart
    request.session.modified = True   # ⭐ IMPORTANT

    return redirect('my_cart')
def my_cart(request):
    cart = request.session.get('cart', [])
    return render(request, 'my_cart.html', {'cart': cart})
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
        return redirect('home')

    item = get_object_or_404(model, id=id)

    if request.method == "POST":
        Order.objects.create(
            user=request.user,
            product_name=item.name,
            product_image=item.image,
            price=item.price,
            quantity=1,
            status="Pending"
        )
        return redirect('success')

    return render(request, 'payment.html', {'item': item})


# wrappers
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


# ================= LOGOUT =================
def user_logout(request):
    logout(request)
    return redirect('home')