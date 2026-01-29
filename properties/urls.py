from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('completed/', views.property_completed, name='property_completed'),
    path('completed/<int:pk>/edit/', views.property_completed_edit, name='property_completed_edit'),
    path('excel/', views.excel_import_export, name='excel_import_export'),
    path('excel/import/', views.excel_import, name='excel_import'),
    path('excel/export/', views.excel_export, name='excel_export'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('create/', views.property_create, name='property_create'),
    path('<int:pk>/admin-edit/', views.property_admin_edit, name='property_admin_edit'),
    path('<int:pk>/user-edit/', views.property_user_edit, name='property_user_edit'),
    path('<int:pk>/delete/', views.property_delete, name='property_delete'),
    path('<int:pk>/upload-image/', views.property_upload_image, name='property_upload_image'),
    path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),
]
