from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, Order
import os
from django.conf import settings
from django.http import HttpResponse
def serve_sw(request):
    path = os.path.join(settings.BASE_DIR, 'bot_app', 'static', 'sw.js')
    with open(path, 'r', encoding='utf-8') as f:
        return HttpResponse(f.read(), content_type='application/javascript')

# --- MIJOZLAR UCHUN SAHIFALAR ---

def home_page(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # Agar kategoriya bo'yicha filtr qilinsa
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'categories': categories,
        'products': products,
        'selected_category': int(category_id) if category_id else None
    }
    return render(request, 'index.html', context)


def create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Formadan ma'lumotlarni olish
        client_name = request.POST.get('client_name')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        order_amount = request.POST.get('order_amount')

        # Yangi buyurtmani bazaga saqlash
        new_order = Order.objects.create(
            product=product,
            client_name=client_name,
            phone=phone,
            location=location,
            order_amount=order_amount,
            status='yangi'
        )

        # Mijozni kelajakda tanib olish uchun raqamini sessiyaga yozib qo'yamiz
        request.session['user_phone'] = phone

        # Buyurtma berilgach, mijozni to'g'ridan-to'g'ri uning buyurtmalari sahifasiga yo'naltiramiz
        return redirect('success.html')

    # GET so'rovi bo'lsa, xarid qilish formasini ko'rsatamiz
    return render(request, 'order_form.html', {'product': product})

# --- MAXSUS ADMIN PANEL (Django admindan tashqari) ---

def custom_admin_dashboard(request):
    orders = Order.objects.all().order_by('-id')
    products = Product.objects.all().order_by('-id')
    categories = Category.objects.all()

    context = {
        'orders': orders,
        'products': products,
        'categories': categories,
    }
    return render(request, 'admin_dashboard.html', context)


def admin_add_product(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = get_object_or_404(Category, id=category_id)

        Product.objects.create(
            category=category,
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            image=request.FILES.get('image')  # Rasmni yuklash
        )
        return redirect('custom_admin')

    categories = Category.objects.all()
    return render(request, 'admin_add_product.html', {'categories': categories})
def custm_admin_dashboard(request):
    # Faqat 'yetkazildi' bo'lmagan buyurtmalarni olamiz
    orders = Order.objects.exclude(status='yetkazildi')
    return render(request, 'admin_dashboard.html', {'orders': orders})
def my_orders(request):
    # Mijoz o'z raqami orqali kirgan deb faraz qilamiz
    phone = request.session.get('user_phone')
    orders = Order.objects.filter(phone=phone).exclude(status='yetkazildi')
    return render(request, 'my_orders.html', {'my_orders': orders})

def mark_as_delivered(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'yetkazildi'
    order.save()
    return redirect('my_orders')


def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')

        if new_status == 'yetkazildi':
            # Agar status 'yetkazildi' bo'lsa, bazadan o'chirib tashlaymiz
            order.delete()
        else:
            # Aks holda statusni yangilaymiz
            order.status = new_status
            order.save()

    return redirect('custom_admin')  # Admin panel nomingizni yozing