from django.contrib import admin
from .models import Pet, AdoptionRequest, SuccessStory, Message

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'pet_type', 'breed', 'age', 'vaccination_status', 'owner', 'location', 'created_at')
    list_filter = ('pet_type', 'vaccination_status', 'location')
    search_fields = ('name', 'breed', 'location')
    list_per_page = 25

@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('pet', 'adopter', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('pet__name', 'adopter__username')
    list_per_page = 25

@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ('pet', 'adopter', 'created_at')
    search_fields = ('pet__name', 'adopter__username', 'story')
    list_per_page = 25

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'pet', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__username', 'receiver__username', 'pet__name', 'content')
    list_per_page = 25