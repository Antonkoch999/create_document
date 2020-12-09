from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'input'

urlpatterns = [
    path('', views.start_page, name='start_page'),
    path('input/<int:id_>/', views.create_documents, name='detail_page'),
    path('create_client/', views.create_client, name='create_client'),
    path('register/', views.register, name='register'),
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('send/', views.send_mail, name='send_mail'),
]
