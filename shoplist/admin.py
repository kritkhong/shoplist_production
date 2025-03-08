from django.contrib import admin
from .models import Product, SaleSession, Image
# Register your models here.

admin.site.register(Product)
admin.site.register(SaleSession)
admin.site.register(Image)
