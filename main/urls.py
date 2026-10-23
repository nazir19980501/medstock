from django.urls import path
from . import views
app_name='main'
urlpatterns=[path('',views.dashboard,name='dashboard'),path('medicines/',views.medicine_list,name='medicine_list'),path('medicines/add/',views.medicine_create,name='medicine_create'),path('medicines/<int:pk>/edit/',views.medicine_edit,name='medicine_edit'),path('medicines/<int:pk>/delete/',views.medicine_delete,name='medicine_delete'),path('sales/',views.sales,name='sales'),path('reports/',views.reports,name='reports'),path('sales/new/',views.sale_create,name='sale_create')]
