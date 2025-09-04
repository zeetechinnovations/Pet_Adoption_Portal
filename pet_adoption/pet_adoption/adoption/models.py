from django.db import models
from django.contrib.auth.models import User

class Pet(models.Model):
    PET_TYPES = [
        ('dog', 'Dog'), ('cat', 'Cat'), ('rabbit', 'Rabbit'), ('hamster', 'Hamster'),
        ('birds', 'Birds'), ('fish', 'Fish'), ('turtle', 'Turtle'), ('snake', 'Snake'),
        ('horse', 'Horse'), ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    vaccination_status = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='pets/', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    pet_type = models.CharField(max_length=10, choices=PET_TYPES)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_adopted(self):
        return self.adoptionrequest_set.filter(status='approved').exists()

class AdoptionRequest(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    adopter = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class SuccessStory(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    adopter = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', 'created_at']


    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} about {self.pet.name}"