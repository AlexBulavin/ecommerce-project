from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group, User
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm #Импортируем встроенную форму аутентификации Djando
from django.contrib.auth import login, authenticate, logout #Импортируем нативные модули логина и аутентификации Djando

# Create your views here.

def home(request, category_slug=None):
    category_page = None
    products = None
    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category_page, available=True)
    else:
        products = Product.objects.all().filter(available=True)
    return render(request, 'home.html', {'category': category_page, 'products': products})


def product(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    return render(request, 'product.html', {'product': product})

def carttest(request):
    return render(request, 'carttest.html')


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        cart_item.save()

    return redirect('cart_detail')

def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter))

def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')


def cart_delete(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_detail')

# def signUpView(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.clean_data.get('username')
#             signup_user = User.objects.get(username=username)
#             user_group = Group.objects.get(name='User')
#             user_group.user_set.add(signup_user)
#     else:
#         form = SignUpForm()
#     return render(request, 'signup.html', {'form': form})

def signUpView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            user_group = Group.objects.get(name='User')
            user_group.user_set.add(signup_user)

    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def loginView(request):
    if request.method == 'POST': #Проверяем, равен ли request метод POST
        form = AuthenticationForm(data=request.POST) #Если да, то создаём переменную form и передаём в неё значение AuthenticationForm(request.POST)
        #Проверяем валидность формы:
        if form.is_valid():
            #Если валидна, то создаём переменные username и password и передаём в них значения
            username = request.POST['username']
            password = request.POST['password']
            #Создаём credentials
            user = authenticate(username=username, password=password)
            #Проверяем, существует ли пользователь, то есть не отсутствует ли он
            if user is not None:
                #Пропускаем пользователя на логин
                login(request, user)
                #Перенаправляем пользователя на главную страницу
                return redirect('home')
            #Иначе (если пользователь не существует), перенаправляем его на странизу SignUp
            else:
                return redirect('signup')
    #Если метод не POST, присваиваем пустую форму
    else:
        #Создаём пустую форму
        form = AuthenticationForm()
        #И передаём её в login.html
        return render(request, 'login.html', {'form': form})

def signoutView(request):
    logout(request)
    return redirect('login')



