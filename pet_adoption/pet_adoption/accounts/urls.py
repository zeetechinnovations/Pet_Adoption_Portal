from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('logout/',views.logout_view, name='logout'),
    path('reset-password/<int:user_id>/<str:token>/', views.reset_password, name='reset_password'),

]