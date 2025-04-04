from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index2', views.index2, name='index2'),
    # path('test', views.test, name='test'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('order/<int:id>', views.order_detail, name='orderdetail'),
    path('addorder', views.add_order, name='addorder'),
    path('addfabricpurchased/<int:id>', views.add_fabricpurchased, name='addfabricpurchased'),
    path('addprintinganddyeing/<int:id>', views.add_printinganddyeing, name='addprintinganddyeing'),
    path('addclothcutting/<int:id>', views.add_clothcutting, name='addclothcutting'),
    path('addstitching/<int:id>', views.add_stitching, name='addstitching'),
    path('addextrawork/<int:id>', views.add_extrawork, name='addextrawork'),
    path('addfinishingandpacking/<int:id>', views.add_finishingandpacking, name='addfinishingandpacking'),
    path('adddispatch/<int:id>', views.add_dispatch, name='adddispatch'),

    path('filter/<str:status>', views.filter_by_status, name='filter_by_status'),
]