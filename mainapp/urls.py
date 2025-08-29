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
    path('addprintinganddyeingsent/<int:id>', views.add_printinganddyeingsent, name='addprintinganddyeingsent'),
    path('addprintinganddyeingreceived/<int:id>', views.add_printinganddyeingreceived, name='addprintinganddyeingreceived'),
    path('addclothcutting/<int:id>', views.add_clothcutting, name='addclothcutting'),
    path('addstitching/<int:id>', views.add_stitching, name='addstitching'),
    path('addextrawork/<int:id>', views.add_extrawork, name='addextrawork'),
    path('addfinishingandpacking/<int:id>', views.add_finishingandpacking, name='addfinishingandpacking'),
    path('adddispatch/<int:id>', views.add_dispatch, name='adddispatch'),

    path('filter/<str:status>', views.filter_by_status, name='filter_by_status'),
    path('search', views.search_orders, name='search_orders'),

    path('trackdyers', views.track_dyers, name='track_dyers'),
    path('trackfabrics', views.track_fabrics, name='track_fabrics'),
    path('export/<str:timespan>', views.export_orders_csv, name='export_orders_csv'),
]