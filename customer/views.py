from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import date, datetime
from shoplist.models import SaleSession, Product, Image
from natsort import natsorted

# Create your views here.


def index(request):
    latest_sale = str(SaleSession.objects.order_by("-sale_date")[0])
    return redirect(reverse('customer:code_ref', kwargs={'sale_date_str': latest_sale}))


def code_ref(request, sale_date_str):
    sale_date_obj = datetime.strptime(sale_date_str, "%d-%m-%Y").date()
    sale_date = SaleSession.objects.get(sale_date=sale_date_obj)
    product_list = Product.objects.filter(
        sale_date=sale_date).filter(order_amount__gt=0)
    product_list = natsorted(product_list, key=lambda o: o.sale_code)
    context = {
        "product_list": product_list,
        "this_session": sale_date,
    }
    return render(request, "customer/customer_ref.html", context)
