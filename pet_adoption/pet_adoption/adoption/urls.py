from django.urls import path
from . import views

app_name = 'adoption'
urlpatterns = [
    path('', views.home, name='home'),
    path('pets/', views.pet_list, name='pet_list'),
    path('pet/<int:pk>/', views.pet_detail, name='pet_detail'),
    path('pet/add/', views.pet_form, name='pet_form'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('success-stories/', views.success_stories, name='success_stories'),
    path('pet/<int:pk>/apply/', views.apply_adoption, name='apply_adoption'),
    path('request/<int:pk>/approve/', views.approve_adoption, name='approve_adoption'),
    path('request/<int:pk>/reject/', views.reject_adoption, name='reject_adoption'),
    path('messages/<int:pet_pk>/', views.messages, name='messages'),
    path('pet/<int:pet_id>/applicants/', views.applicants_list, name='applicants'),
    path('messages/edit/<int:message_id>/', views.edit_message, name='edit_message'),
]