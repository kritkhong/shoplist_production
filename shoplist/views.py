from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import SaleSession, Product, Image
from django.urls import reverse
from django.db.models import F
from datetime import date, datetime
from natsort import natsorted
from django.views.generic.edit import FormView
from django.contrib import messages
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import NewSessionForm, AddPhotoForm
from .utils import get_session_info
import re


@login_required(login_url='/users/login')
def index(request):
    lastest_sale = str(SaleSession.objects.order_by("-sale_date")[0])
    filter = 'buying'
    return HttpResponseRedirect(reverse('shoplist:buying_list', args=[lastest_sale, filter]))


@login_required(login_url='/users/login')
def buying_list(request, sale_date_str, filter):
    sale_date_obj = datetime.strptime(sale_date_str, "%d-%m-%Y").date()
    sale_date = SaleSession.objects.get(sale_date=sale_date_obj)
    product_list = Product.objects.filter(sale_date=sale_date)
    if filter == 'buying':
        product_list = product_list.filter(bought_amount__lt=F('order_amount'))
    elif filter == 'done':
        product_list = product_list.filter(
            bought_amount__gte=F('order_amount')).exclude(bought_amount=0)
    elif filter == 'no_sale':
        product_list = product_list.filter(
            order_amount=0).exclude(bought_amount__gt=0)

    product_list = natsorted(product_list, key=lambda o: o.sale_code)
    all_session = SaleSession.objects.all().order_by(
        "-sale_date")  # for user to select
    context = {
        "product_list": product_list,
        "sessions": all_session,
        "this_session": sale_date,
        "filter": filter
    }
    return render(request, "shoplist/buy_list.html", context)


@login_required(login_url='/users/login')
def create_session(request):
    if request.method == 'POST':
        form = NewSessionForm(request.POST, request.FILES)
        if form.is_valid():
            input_date = form.cleaned_data["sale_date"]
            try:
                sale_session = SaleSession.objects.get(sale_date=input_date)
                messages.error(request,
                               'Sale session already existed, use "Update" instead.')
                return HttpResponseRedirect(reverse('shoplist:buying_list', args=[str(sale_session), 'buying']))
            except ObjectDoesNotExist:
                sale_session = SaleSession.objects.create(sale_date=input_date)

            product_list = get_session_info(sale_session.sale_date)
            for code, caption, count in product_list:
                product_obj = Product.objects.create(
                    sale_date=sale_session,
                    sale_code=code,
                    description_text=caption,
                    order_amount=count,
                )

            files = form.cleaned_data['images']
            for f in files:
                if f.content_type.startswith('image'):
                    if ' copy' in f.name:
                        continue

                    code_regex = r'([A-Z]\d{2,3}(_\d+)?)'
                    matches = re.findall(code_regex, f.name)
                    if matches:
                        img_obj_created = False
                        i = None
                        for match in matches:
                            code = match[0]
                            try:
                                p = Product.objects.get(
                                    sale_date=sale_session, sale_code=code)
                                if not img_obj_created:
                                    i = Image.objects.create(
                                        sale_date=sale_session, image=f)
                                    img_obj_created = True
                                    print(f'++image object created [{i}]++')
                                p.image = i
                                p.save()
                                print(f'++ matched [{p}] with [{i}]++')
                            except ObjectDoesNotExist:
                                print(
                                    f'-- [{f.name}] does not match any product in current session--')

            return HttpResponseRedirect(reverse('shoplist:buying_list', args=[str(sale_session), 'buying']))
    else:
        form = NewSessionForm
        return render(request, "shoplist/create_session.html", {'form': form})


@login_required(login_url='/users/login')
def buy(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        product_id = request.POST['product_id']
        try:
            product = Product.objects.get(pk=product_id)
            product.bought_amount = F(
                'bought_amount') + int(request.POST['buy_amount'])
            product.save()
            product.refresh_from_db()

            ser_instance = serializers.serialize('json', [product, ])
            return JsonResponse({"instance": ser_instance}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"error": 'ObjectDoesNotExist'}, status=400)


@login_required(login_url='/users/login')
def adjust_order(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        product_id = request.POST['product_id']
        try:
            product = Product.objects.get(pk=product_id)
            product.order_amount = F(
                'order_amount') + int(request.POST['order_adjust'])
            product.save()
            product.refresh_from_db()
            ser_instance = serializers.serialize('json', [product, ])
            return JsonResponse({"instance": ser_instance}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"error": 'ObjectDoesNotExist'}, status=400)


@login_required(login_url='/users/login')
def update_buy_list(request):
    sale_session = SaleSession.objects.get(pk=request.POST['sale_date_id'])
    product_list = get_session_info(sale_session.sale_date)
    report = {
        'create_new': ''
    }
    # breakpoint()
    for code, caption, count in product_list:
        try:
            product = Product.objects.get(
                sale_date=sale_session, sale_code=code,)
            product.description_text = caption
            product.order_amount = count
            product.save()
        except ObjectDoesNotExist:
            product = Product.objects.create(
                sale_date=sale_session,
                sale_code=code,
                description_text=caption,
                order_amount=count,
            )
            report['create_new'] += code + ', '
    if report['create_new']:
        messages.info(request, 'New imports: '+report['create_new'])
    return HttpResponseRedirect(reverse('shoplist:buying_list', args=[str(sale_session), 'buying']))


@login_required(login_url='/users/login')
def add_photos(request, session_id):
    sale_session = SaleSession.objects.get(pk=session_id)
    products = Product.objects.filter(
        sale_date=sale_session).filter(image__isnull=True)
    # products without photo
    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['images']
            for f in files:
                if f.content_type.startswith('image'):
                    if ' copy' in f.name:
                        continue

                    code_regex = r'([A-Z]\d{2,3}(_\d+)?)'
                    matches = re.findall(code_regex, f.name)
                    if matches:
                        img_obj_created = False
                        i = None
                        for match in matches:
                            code = match[0]
                            try:
                                p = products.get(sale_code=code)
                                if not img_obj_created:
                                    i = Image.objects.create(
                                        sale_date=sale_session, image=f)
                                    img_obj_created = True
                                    print(f'++image object created [{i}]++')
                                p.image = i
                                p.save()
                                print(f'++ matched [{p}] with [{i}]++')
                            except ObjectDoesNotExist:
                                print(
                                    f'--[{f.name}] does not match any object in current update--')

            return HttpResponseRedirect(reverse('shoplist:buying_list', args=[str(sale_session), 'buying']))
    else:
        form = AddPhotoForm
        context = {
            "sale_session": sale_session,
            "products": products,
            "form": form,
        }
        return render(request, "shoplist/add_photos.html", context)
