from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import HttpResponse, Http404
from datetime import date
from django.db.models import Q

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator
# Used to send mail from within Django
from django.core.mail import send_mail

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

# Imports the Post class
from models import *
from forms import *

import json

# Age helper function
def calculate_age(dob):
    today = date.today()
    offset = ((today.month, today.day) < (dob.month, dob.day)) 
    return today.year - dob.year - offset

@ensure_csrf_cookie
@login_required
def index(request):
    context = {}

    context['posts'] = Post.objects.all().order_by('-id')
    context['form'] = PostForm() 

    return render(request, 'index.html', context)

@ensure_csrf_cookie
@login_required
def follow_stream(request):
    context = {}

    context['form'] = PostForm() 
    following = request.user.profile.following.all().values('user')
    context['posts'] = Post.objects.filter(user__in=following).order_by('-id')

    return render(request, 'following.html', context)

@login_required
def profile(request):
    context = {}

    tempUser = request.GET['user']
    context['user'] = User.objects.get(username__exact=tempUser)
    context['posts'] = Post.objects.filter(user__username=tempUser).order_by('-id')
    if context['user'].profile.dob:
        context['age'] = calculate_age(context['user'].profile.dob)         
    if request.user.profile.following.filter(user=context['user']).exists():
        context['followed'] = True
        context['form'] = UnfollowForm()
    else:
        context['form'] = FollowForm()

    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    context = {}
    context['form'] = PhotoForm()
    context['form1'] = UserForm()
    context['form2'] = ProfileForm()
    context['form3'] = Profile2Form()
    return render(request, 'edit-profile.html', context)

@login_required
@transaction.atomic
def update_profile(request):
    context = {}

    user_form = UserForm(request.POST, instance=request.user)
    profile_form = ProfileForm(request.POST, instance=request.user.profile)
    profile2_form = Profile2Form(request.POST, instance=request.user.profile)
    
    context['form'] = PhotoForm()
    context['form1'] = UserForm()
    context['form2'] = ProfileForm()
    context['form3'] = Profile2Form()
    
    if user_form.is_valid() and profile_form.is_valid() and profile2_form.is_valid():
        user_form.save()
        profile_form.save()
    else:
        context['form1'] = user_form
        context['form2'] = profile_form
        context['form3'] = profile2_form

    return render(request, 'edit-profile.html', context)

@login_required
@transaction.atomic
def update_photo(request):
    context = {}

    context['form1'] = UserForm()
    context['form2'] = ProfileForm()
    context['form3'] = Profile2Form()

    profile = get_object_or_404(Profile, user=request.user)
    if len(request.FILES) == 0:
        profile.photo = None
    form = PhotoForm(request.POST, request.FILES, instance=profile)
    if not form.is_valid():
        context['form'] = form
    else:
        profile.photo_content_type = form.cleaned_data['photo'].content_type
        form.save()
        context['form'] = PhotoForm()
        return redirect(reverse('edit_profile'))

    return render(request, 'edit-profile.html', context)

@login_required
@transaction.atomic
def get_photo(request, id):
    context = {}

    user = get_object_or_404(User, id=id)

    if not user.profile.photo:
        raise Http404

    return HttpResponse(user.profile.photo, content_type=user.profile.photo_content_type)

@login_required
@transaction.atomic
def follow(request, id):
    context = {}

    profile = request.user
    followThis = get_object_or_404(Profile, id=id)

    form = FollowForm(request.POST)
    if not form.is_valid():
        context['form'] = form
    else:
        myUser = User.objects.get(username__exact=form.cleaned_data['profile'])
        followUser = User.objects.get(username__exact=form.cleaned_data['followThis'])
        myUser.profile.following.add(followUser.profile)
        myUser.save()
        context['form'] = UnfollowForm()

    user = followThis.user

    context['user'] = user
    context['posts'] = Post.objects.filter(user=user).order_by('-id')
    if context['user'].profile.dob:
        context['age'] = calculate_age(context['user'].profile.dob) 
    if request.user.profile.following.filter(user=user).exists():
        context['followed'] = True

    return render(request, 'profile.html', context)

@login_required
@transaction.atomic
def unfollow(request, id):
    context = {}

    profile = request.user.profile
    followThis = get_object_or_404(Profile, id=id)

    form = UnfollowForm(request.POST)
    if not form.is_valid():
        context['form'] = form
    else:
        myUser = User.objects.get(username__exact=form.cleaned_data['profile'])
        followUser = User.objects.get(username__exact=form.cleaned_data['followThis'])
        myUser.profile.following.remove(followUser.profile)
        myUser.save()
        context['form'] = FollowForm()

    user = followThis.user

    context['user'] = user
    context['posts'] = Post.objects.filter(user=user).order_by('-id')
    if context['user'].profile.dob:
        context['age'] = calculate_age(context['user'].profile.dob) 
    if request.user.profile.following.filter(user=user).exists():
        context['followed'] = True

    return render(request, 'profile.html', context)

@login_required
@transaction.atomic
def add_post(request):
    context = {}
    
    new_post = Post(text="error",
                    user=request.user)
    form = PostForm(request.POST,
                    initial={'parent': request.POST.get('parent')},
                    instance=new_post)
    if not form.is_valid():
        context['form'] = form
        context['posts'] = Post.objects.all().order_by('-id')
        return render(request, 'index.html', context)
    else:
        form.save()
    
    return redirect(reverse('home')) # Prevent F5 errors + reverse-chrono


@login_required
def add_comment(request):
    context = {}
    
    new_post = Post(text="error",
                    user=request.user)
    form = PostForm(request.POST,
                    initial={
                        'parent': request.POST.get('parent'),
                        'text': request.POST.get('text')
                    },
                    instance=new_post)

    if not form.is_valid():
        context['form'] = form
        context['posts'] = Post.objects.all().order_by('-id')
        return render(request, 'index.html', context)
    else:
        form.save()
    
    response_text = serializers.serialize('json', Post.objects.all())
    response_text2 = serializers.serialize('json', User.objects.all())
    data = { 'posts' : response_text, 'users' : response_text2 }
    output = json.dumps(data)
    return HttpResponse(output, content_type='application/json')


@transaction.atomic
def register(request):
    context = {}

    if request.user.is_authenticated():
        return redirect(reverse('home'))
 
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'])
    # Mark the user as inactive to prevent login before email confirmation.
    new_user.is_active = False
    new_user.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
Welcome to minimal.  Enjoy your stay and be sure to shippost frequently.  
Please click the link below to verify your email address and 
complete the registration of your account: 

  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="benjami1@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'needs-confirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'confirmed.html', {})


def get_posts_json(request):
    response_text = serializers.serialize('json', Post.objects.all())
    response_text2 = serializers.serialize('json', User.objects.all())
    data = { 'posts' : response_text, 'users' : response_text2 }
    output = json.dumps(data)
    return HttpResponse(output, content_type='application/json')

def get_posts_json_followers(request):
    following = request.user.profile.following.all().values('user')
    response_text = serializers.serialize('json', 
                        Post.objects.filter(Q(user__in=following) | ~Q(parent="")))
    response_text2 = serializers.serialize('json', User.objects.all())
    data = { 'posts' : response_text, 'users' : response_text2 }
    output = json.dumps(data)
    return HttpResponse(output, content_type='application/json')

def get_posts_json_profile(request):
    response_text = serializers.serialize('json', Post.objects.all())
    response_text2 = serializers.serialize('json', User.objects.all())
    data = { 'posts' : response_text, 'users' : response_text2 }
    output = json.dumps(data)
    return HttpResponse(output, content_type='application/json')


@login_required
def add_comment_followers(request):
    context = {}
    
    new_post = Post(text="error",
                    user=request.user)
    form = PostForm(request.POST,
                    initial={
                        'parent': request.POST.get('parent'),
                        'text': request.POST.get('text')
                    },
                    instance=new_post)

    if not form.is_valid():
        context['form'] = form
        context['posts'] = Post.objects.all().order_by('-id')
        return render(request, 'index.html', context)
    else:
        form.save()
    
    response_text = serializers.serialize('json', Post.objects.all())
    response_text2 = serializers.serialize('json', User.objects.all())
    data = { 'posts' : response_text, 'users' : response_text2 }
    output = json.dumps(data)
    return HttpResponse(output, content_type='application/json')