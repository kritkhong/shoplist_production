from django.db import models

# Create your models here.


class SaleSession(models.Model):
    sale_date = models.DateField(
        unique=True, auto_now=False, auto_now_add=False)

    def __str__(self):
        return f'{self.sale_date.day}-{self.sale_date.month}-{self.sale_date.year}'


def image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/shoplist/<sale_date>/file_name
    return "shoplist/product_images/{0}/{1}".format(instance.sale_date, filename)


class Image(models.Model):
    sale_date = models.ForeignKey(
        SaleSession, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_path)

    def __str__(self):
        return f"{self.sale_date} {self.image.name.split('/')[-1]}"


class Product(models.Model):
    sale_date = models.ForeignKey(SaleSession, on_delete=models.CASCADE)
    sale_code = models.CharField(max_length=10)
    description_text = models.CharField(max_length=150)
    note = models.CharField(max_length=150, default='')
    bought_amount = models.IntegerField(default=0)
    order_amount = models.IntegerField()
    is_manual = models.BooleanField(default=False)
    image = models.ForeignKey(
        Image, on_delete=models.SET_NULL, blank=True, null=True,)

    def remain(self):
        return self.order_amount - self.bought_amount

    def __str__(self):
        return f'{self.sale_date} [{self.sale_code}] {self.description_text[:20]} {self.bought_amount}/{self.order_amount}'
