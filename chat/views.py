from django.shortcuts import render
from .models import Room
from django.contrib.auth.decorators import login_required

from .forms import UserForm, ProfileForm


def index_view(request):
    return render(request, 'index.html', {
        # sending dynamic room-list through Django Channels
    })


def room_view(request, room_name):
    chat_room, created = Room.objects.get_or_create(name=room_name)
    return render(request, 'room.html', {
        'room': chat_room,
    })


@login_required
def settings(request):
    if request.method == 'POST':
        user_form = UserForm(instance=request.user, data=request.POST)
        profile_form = ProfileForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'settings.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'user': request.user})
