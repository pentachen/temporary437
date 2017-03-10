from django import forms
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from models import *
from datetime import date

MAX_UPLOAD_SIZE = 2097152

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo',)

    def clean_photo(self):
        picture = self.cleaned_data['photo']
        if not picture:
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is 2MB)')
        return picture

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput())
    username   = forms.CharField(max_length = 20)
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username


    # Customizes form validation for the email field.
    def clean_email(self):
        # Confirms that the email is not already present in the
        # User model database.
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError("An account with this email already exists.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return email

class FollowForm(forms.Form):
    followThis = forms.CharField(max_length = 20)
    profile = forms.CharField(max_length = 20)


    def clean(self):
        cleaned_data = super(FollowForm, self).clean()

        followThis = cleaned_data.get('followThis')
        profile = cleaned_data.get('profile')
        
        followThisUser = None
        myUser = None
        try:
            followThisUser = User.objects.get(username__exact=followThis)
            myUser = User.objects.get(username__exact=profile)
        except User.DoesNotExist:
            raise forms.ValidationError("Cannot follow user: user not found.")
        
        myP = myUser.profile

        if myP.following.filter(user=followThisUser).exists():
            raise forms.ValidationError("Cannot follow user: already following user.")
        # We must return the cleaned data we got from our parent.
        return cleaned_data


class UnfollowForm(forms.Form):
    followThis = forms.CharField(max_length = 20)
    profile = forms.CharField(max_length = 20)

    def clean(self):
        cleaned_data = super(UnfollowForm, self).clean()

        followThis = cleaned_data.get('followThis')
        profile = cleaned_data.get('profile')
        
        followThisUser = None
        myUser = None
        try:
            followThisUser = User.objects.get(username__exact=followThis)
            myUser = User.objects.get(username__exact=profile)
        except User.DoesNotExist:
            raise forms.ValidationError("Cannot unfollow user: user not found.")
        
        myP = myUser.profile

        if not myP.following.filter(user=followThisUser).exists():
            raise forms.ValidationError("Cannot unfollow user: not following user.")
        # We must return the cleaned data we got from our parent.
        return cleaned_data


class UserForm(forms.ModelForm):
    first_name = forms.CharField(max_length = 20,
                                 label='first name')
    last_name = forms.CharField(max_length = 20,
                                 label='last name')

    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) > 20:
            raise forms.ValidationError("First name must be under 20char")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) > 20:
            raise forms.ValidationError("Last name must be under 20char")
        return last_name

class ProfileForm(forms.ModelForm):
    bio = forms.CharField(max_length = 430,
                          widget=forms.Textarea,
                          label='bio')

    class Meta:
        model = Profile
        fields = ('bio',)

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if len(bio) > 430:
            raise forms.ValidationError("Bio cannot be over 430 characters")
        return bio

class DateInput(forms.DateInput):
    input_type = 'date'

class Profile2Form(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('dob',)
        widgets = {
            'dob': DateInput()
        }

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if not dob:
            raise forms.ValidationError("You must enter a birthday.")            
        if date.today() <= dob:
            raise forms.ValidationError("No time travellers/world-line hoppers allowed")
        return dob

class PostForm(forms.ModelForm):
    text = forms.CharField(max_length = 160,
                          widget=forms.Textarea,
                          label='')
    parent = forms.CharField(max_length = 100,
                            label='',
                            required=False,
                            widget=forms.HiddenInput())


    text.widget.attrs['class'] = 'post-area'

    class Meta:
        model = Post
        fields = ('text', 'parent')

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) > 160:
            raise forms.ValidationError("Posts must be 160char or less.")
        if len(text) == 0:
            raise forms.ValidationError("Posts cannot be empty.")
        return text

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent != "":
            if len(parent) > 100:
                raise forms.ValidationError("wot in tarnation (parent id too long)")
            if not Post.objects.filter(id=parent).exists():
                raise forms.ValidationError("Parent post does not exist.")
        return parent