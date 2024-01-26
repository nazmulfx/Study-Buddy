from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from . models import Room, Topic, Message, User
from . form import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist.')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'incorrect username or password')
        
    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)              # hold for a bit (commit=False)
            user.username = user.username.lower()       # saving username as lowercase
            user.save()                                 # then saving the user data
            login(request, user)                        # then registered user loged in & will be redirect to home
            return redirect('home')
        else:
            messages.error(request, 'An error occurrd during registration.')
            
    context = {'page':page, 'form':form}
    return render(request, 'base/login_register.html', context)

def home(request):
    # if request.GET.get('q') != None:
    #     q = request.GET.get('q')
    # else:
    #     q = ''
    q = request.GET.get('q') if request.GET.get('q') != None else ''    # used inline if statement
    rooms = Room.objects.filter(                                        # Q models allow to multiple search funcnality by adding AND / OR
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )[0:99]                                                             # filtered [0:10], maximum 10 rooms will return
    room_count = rooms.count()
    topics = Topic.objects.all()[0:5]                                   # by [0:5] we limited it, will query maximum 5 topics
    total_room = Room.objects.all().count()
    
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:99]
    
    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages, 'total_room':total_room}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()                      # order_by('-create')  # decending order by create value
    participants = room.participants.all()                      # getting all participants in this current room id=pk 
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,                # current loged in user
            room = room,                        # current room, using room - id=pk
            body = request.POST.get('body'),    # taken from html input field name 'body'
        )
        room.participants.add(request.user)     # after message a user in a room, user addd in participants
        return redirect('room', pk=room.id)     # redirecting to same room, pk= current room id
    
    context = {'room':room, 'room_messages':room_messages, 'participants':participants}    
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)   # get_or_create actually do, if new objects create=True, if already in db topic=True & created=False
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('home')
    
    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.user != room.host:                               # only room creator can update and delete this room
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    
    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:                               # only room creator can update and delete this room
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    context = {'obj':room}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    context = {'obj':message}
    return render(request, 'base/delete.html', context)

@login_required(login_url="login")
def updateUser(request):
    # no need pk value, because i will update current loged in user
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    
    context = {'form':form}
    return render(request, 'base/update-user.html', context)


def topicPage(request):
    # if request.GET.get('q') != None:
    #     q = request.GET.get('q')
    # else:
    #     q = ''
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    total_room = Room.objects.all().count()
    
    context = {'topics':topics, 'total_room':total_room}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()[0:99]
    context = {'room_messages':room_messages}
    return render(request, 'base/activity.html', context)