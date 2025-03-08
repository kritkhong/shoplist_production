from django.urls import path

from . import views

app_name = 'shoplist'
urlpatterns = [
    path("", views.index, name="index"),
    path('list/<str:sale_date_str>/<str:filter>',
         views.buying_list, name='buying_list'),
    path('buy', views.buy, name='buy'),
    path('new/session', views.create_session, name='create_session'),
    path('update', views.update_buy_list, name='update_buy_list'),
    path('adjust', views.adjust_order, name='adjust'),
    path('add_photos/<int:session_id>', views.add_photos, name='add_photos'),
]
