from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")

    def __annotations__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Kategoriyalar"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Kategoriyasi")
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    price = models.CharField(max_length=100, verbose_name="Narxi")
    image = models.ImageField(upload_to='products/', verbose_name="Rasmi", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Mahsulotlar"
class Status(models.Model):
    STATUS_CHOICES = (
        ('yangi', 'Yangi'),
        ('tayyorlanmoqda', 'Tayyorlanmoqda'),
        ('yolda', "Yo'lda 🚚"),
        ('yetkazildi', 'Yetkazildi ✅'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='yangi')
class Order(models.Model):
    client_name = models.CharField(max_length=200, verbose_name="Mijoz ismi")
    phone = models.CharField(max_length=50, verbose_name="Telefon raqami")
    extra_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Qo'shimcha tel")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Mahsulot")
    order_amount = models.CharField(max_length=100, verbose_name="Xohlagan ulush summasi")
    location = models.CharField(max_length=500, verbose_name="Manzil / Lokatsiya")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kelgan vaqti")
    status = models.CharField(max_length=20, default='yangi')

    class Meta:
        verbose_name_plural = "Buyurtmalar"