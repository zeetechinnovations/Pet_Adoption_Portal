import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.mail import send_mail
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Pet, AdoptionRequest, SuccessStory, Message, User
from .forms import PetForm, MessageForm
from django.contrib import messages as django_messages
from django.http import JsonResponse

# Set up logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

@login_required
def pet_list(request):
    pets = Pet.objects.all()
    pet_type = request.GET.get('pet_type')
    location = request.GET.get('location')
    if pet_type:
        pets = pets.filter(pet_type=pet_type)
    if location:
        pets = pets.filter(location__icontains=location)
    return render(request, 'pet_list.html', {'pets': pets})

@login_required
def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    return render(request, 'pet_detail.html', {'pet': pet})

@login_required
def pet_form(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            if pet.photo:
                image = Image.open(pet.photo)
                image = image.resize((800, 800), Image.Resampling.LANCZOS)
                output = BytesIO()
                image.save(output, format='JPEG', quality=85)
                output.seek(0)
                pet.photo = InMemoryUploadedFile(output, 'ImageField', f"{pet.photo.name.split('.')[0]}.jpg", 'image/jpeg', output.getbuffer().nbytes, None)
            pet.save()
            return redirect('adoption:pet_list')
    else:
        form = PetForm()
    return render(request, 'pet_form.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_authenticated:
        owned_pets = Pet.objects.filter(owner=request.user)
        adoption_requests = AdoptionRequest.objects.filter(adopter=request.user)
        owner_requests = AdoptionRequest.objects.filter(pet__owner=request.user)
        return render(request, 'dashboard.html', {
            'owned_pets': owned_pets,
            'adoption_requests': adoption_requests,
            'owner_requests': owner_requests
        })
    return redirect('accounts:login')

@login_required
def apply_adoption(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.user == pet.owner:
        return redirect('adoption:pet_detail', pk=pk)
    if request.method == 'POST':
        AdoptionRequest.objects.create(pet=pet, adopter=request.user)
        send_mail(
            'New Adoption Request',
            f'A new adoption request has been submitted for your pet {pet.name} by {request.user.username}.',
            'from@example.com',
            [pet.owner.email],
            fail_silently=False,
        )
        return redirect('adoption:dashboard')
    return render(request, 'pet_detail.html', {'pet': pet})

@login_required
def approve_adoption(request, pk):
    adoption_request = get_object_or_404(AdoptionRequest, pk=pk)
    if request.user == adoption_request.pet.owner and request.method == 'POST':
        adoption_request.status = 'approved'
        adoption_request.save()
        SuccessStory.objects.create(pet=adoption_request.pet, adopter=adoption_request.adopter, story="Adoption approved!")
        send_mail(
            'Adoption Request Approved',
            f'Your adoption request for {adoption_request.pet.name} has been approved!',
            'from@example.com',
            [adoption_request.adopter.email],
            fail_silently=False,
        )
        return redirect('adoption:applicants', pet_id=adoption_request.pet.pk)
    return redirect('adoption:dashboard')

@login_required
def reject_adoption(request, pk):
    adoption_request = get_object_or_404(AdoptionRequest, pk=pk)
    if request.user == adoption_request.pet.owner and request.method == 'POST':
        adoption_request.status = 'rejected'
        adoption_request.save()
        send_mail(
            'Adoption Request Rejected',
            f'Your adoption request for {adoption_request.pet.name} has been rejected.',
            'from@example.com',
            [adoption_request.adopter.email],
            fail_silently=False,
        )
        return redirect('adoption:applicants', pet_id=adoption_request.pet.pk)
    return redirect('adoption:dashboard')

@login_required
def messages(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk)
    chat_messages = Message.objects.filter(pet=pet).filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).order_by('-is_pinned', 'created_at')

    can_send_messages = (
        request.user == pet.owner
        or chat_messages.filter(receiver=request.user).exists()
        or AdoptionRequest.objects.filter(pet=pet, adopter=request.user, status='approved').exists()
    )

    recipient = None
    if request.user == pet.owner:
        approved_request = AdoptionRequest.objects.filter(pet=pet, status='approved').first()
        if approved_request:
            recipient = approved_request.adopter
    else:
        recipient = pet.owner

    has_pinned_messages = chat_messages.filter(is_pinned=True).exists()

    if request.method == 'POST':
        logger.info(f"POST request to /messages/{pet_pk}/ with data: {request.POST}")
        # Handle pin/unpin request
        if 'pin_message_id' in request.POST:
            try:
                message_id = request.POST.get('pin_message_id')
                message = get_object_or_404(Message, id=message_id, sender=request.user)
                message.is_pinned = not message.is_pinned
                message.save()
                return JsonResponse({
                    'success': True,
                    'is_pinned': message.is_pinned
                })
            except Message.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Message not found or you are not authorized.'}, status=403)
            except Exception as e:
                logger.error(f"Error pinning/unpinning message {message_id}: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        # Handle delete request
        if 'delete_message_id' in request.POST:
            try:
                message_id = request.POST.get('delete_message_id')
                message = get_object_or_404(Message, id=message_id, sender=request.user)
                message.delete()
                return JsonResponse({'success': True})
            except Message.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Message not found or you are not authorized.'}, status=403)
            except Exception as e:
                logger.error(f"Error deleting message {message_id}: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        # Handle message sending
        form = MessageForm(request.POST)
        if form.is_valid() and can_send_messages:
            message = form.save(commit=False)
            message.sender = request.user
            message.pet = pet
            if request.user == pet.owner:
                approved_request = AdoptionRequest.objects.filter(pet=pet, status='approved').first()
                if approved_request:
                    message.receiver = approved_request.adopter
                else:
                    django_messages.error(request, "No approved adopter found for this pet.")
                    return redirect('adoption:messages', pet_pk=pet.pk)
            else:
                message.receiver = pet.owner
            if message.receiver:
                message.save()
                send_mail(
                    'New Message Received',
                    f'You have received a new message regarding {pet.name} from {message.sender.username}.',
                    'from@example.com',
                    [message.receiver.email],
                    fail_silently=False,
                )
                django_messages.success(request, "Your message was sent!")
            return redirect('adoption:messages', pet_pk=pet.pk)
    else:
        form = MessageForm()

    return render(request, 'messages.html', {
        'pet': pet,
        'chat_messages': chat_messages,
        'form': form,
        'can_send_messages': can_send_messages,
        'recipient': recipient,
        'has_pinned_messages': has_pinned_messages,
    })

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            message.content = content
            message.save()
            django_messages.success(request, "Message updated successfully!")
        else:
            django_messages.error(request, "Message content cannot be empty.")
        return redirect('adoption:messages', pet_pk=message.pet.pk)
    return redirect('adoption:messages', pet_pk=message.pet.pk)

@login_required
def applicants_list(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.user != pet.owner:
        return redirect('adoption:dashboard')
    applicants = AdoptionRequest.objects.filter(pet=pet)
    return render(request, 'applicants.html', {'pet': pet, 'applicants': applicants})

def success_stories(request):
    stories = SuccessStory.objects.all()
    return render(request, 'success_stories.html', {'stories': stories})

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count

@staff_member_required
def analytics_dashboard(request):
    pet_types = Pet.objects.values('pet_type').annotate(count=Count('id'))
    adoption_stats = AdoptionRequest.objects.values('status').annotate(count=Count('id'))
    user_activity = User.objects.annotate(pet_count=Count('pet'), request_count=Count('adoptionrequest')).order_by('-pet_count')[:10]
    return render(request, 'analytics_dashboard.html', {
        'pet_types': pet_types,
        'adoption_stats': adoption_stats,
        'user_activity': user_activity,
    })