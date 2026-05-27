from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from bot_app import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Mijozlar uchun
    path('', views.home_page, name='home'),
    path('order/<int:product_id>/', views.create_order, name='create_order'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('mark-as-delivered/<int:order_id>/', views.mark_as_delivered, name='mark_as_delivered'),

    # Siz uchun maxsus Admin Panel
    path('my-admin/', views.custom_admin_dashboard, name='custom_admin'),
    path('my-admin/add-product/', views.admin_add_product, name='admin_add_product'),

    # FAQAT BITTA TO'G'RI YO'L (Statik fayl sifatida)
    path('sw.js', views.serve_sw, name='sw.js'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)