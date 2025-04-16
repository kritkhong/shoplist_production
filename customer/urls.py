from django.urls import path
from . import views


app_name = 'customer'

urlpatterns = [
    path('', views.index, name="index"),
    path('ref/<str:sale_date_str>', views.code_ref, name='code_ref'),
]
