from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Mahsulot nomi")
    price = models.CharField(max_length=100, verbose_name="Narxi")
    image_id = models.CharField(max_length=255, verbose_name="Telegram Rasm ID")

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return self.name

class Order(models.Model):
    user_id = models.BigIntegerField(verbose_name="Mijoz ID")
    username = models.CharField(max_length=150, blank=True, null=True, verbose_name="Telegram Username")
    client_name = models.CharField(max_length=255, verbose_name="Mijoz ismi")
    phone = models.CharField(max_length=50, verbose_name="Telefon raqami")
    product_name = models.CharField(max_length=255, verbose_name="Sotib olingan mahsulot")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Buyurtma vaqti")

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self):
        return f"{self.client_name} - {self.product_name}"