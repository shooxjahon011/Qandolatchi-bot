"""
URL configuration for config project.
"""
import threading
from django.contrib import admin
from django.urls import path
from bot_app.views import telegram_webhook, bot  # views.py dan kerakli qismlarni import qilamiz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', telegram_webhook),  # Bot webhook manzili
]

# --- PYCHARM-DA TEST REJIMI (POLLING) ---
# Django server yoqilishi bilan bot orqa fonda tinimsiz xabarlarni eshitishni boshlaydi
print("=== TELEGRAM BOT ISHGA TUSHDI (POLLING) ===")
threading.Thread(target=bot.infinity_polling, daemon=True).start()