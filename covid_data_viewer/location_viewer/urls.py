from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:location_id>/', views.detail, name='location_detail'),
    path('add/<int:location_id>', views.add, name='add'),
    path('add/', views.add, name='add'),
    path('delete/<int:location_id>', views.delete, name='delete'),
]