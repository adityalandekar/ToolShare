"""
Definition of forms.
"""


from django import forms
from django.contrib.auth.models import User
from app.models import UserProfile
from app.models import Tool
from app.models import Shed
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput(attrs={
                                   'autofocus': 'autofocus',
                                   'class': 'form-control',
                                   'placeholder': 'User name'}
                               ))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'Password'}))


class LoginForm(forms.Form):
    username = forms.CharField(max_length=24, widget=forms.TextInput(attrs={'autofocus': 'autofocus','class':'form-control','style':'width:100%'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style':'width:100%','class':'form-control'}))

    def clean_password(self):
        message = self.cleaned_data['password']
        num_words = len(message)
        print(num_words)
        if num_words < 6:
            raise forms.ValidationError('The password should be longer than 6 characters.')
        elif num_words > 24:
            raise forms.ValidationError('The password should be shorter than 25 characters.')


class RegisterUserForm(forms.Form):
    MALE = 'Male'
    FEMALE = 'Female'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    HOME = 'Home'
    SHED = 'Shed'

    PICKUP_ARRANGEMENT_CHOICES = (
        (HOME, 'Home'),
        (SHED, 'Shed'),
    )

    first_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'autofocus': 'autofocus','class':'form-control','style':'width:100%'}))
    last_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'style':'width:100%','class':'form-control'}))
    address = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'style':'width:100%','class':'form-control'}))
    zipcode = forms.CharField(max_length=5,widget=forms.TextInput(attrs={'class':'form-control','style':'width:100%'}))
    gender = forms.ChoiceField(widget=forms.RadioSelect(attrs={'style':'list-style-type:none'}), choices=GENDER_CHOICES)
    e_mail = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control','style':'width:100%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','style':'width:100%'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','style':'width:100%'}))

    def clean_first_name(self):
        text = self.cleaned_data['first_name']
        if any(char.isdigit()for char in text):
            raise forms.ValidationError("First name should not contain numbers.")

    def clean_last_name(self):
        text = self.cleaned_data['last_name']
        num_words = len(text)
        if any(char.isdigit()for char in text):
            raise forms.ValidationError("First name should not contain numbers.")

    def clean_password(self):
        text = self.cleaned_data['password']
        num_words = len(text)
        if num_words < 6:
            raise forms.ValidationError("Password is too short.")

    def clean_username(self):
        text = self.cleaned_data['username']
        print(text)
        print('in the try')
        if User.objects.filter(username=text):
            raise forms.ValidationError('Username has already been registered.')


class RegisterToolForm(forms.Form):

    COMMON_USE = 'Common Use'
    GARDENING = 'Gardening'
    WOOD_WORKING = 'Wood Working'
    METAL_WORKING = 'Metal Working'
    CLEANING = 'Cleaning'
    KITCHEN = 'Kitchen'
    OTHERS = 'Others'

    CATEGORY_CHOICES = (
        (COMMON_USE, 'Common Use'),
        (GARDENING, 'Gardening'),
        (WOOD_WORKING, 'Wood Working'),
        (METAL_WORKING, 'Metal Working'),
        (CLEANING, 'Cleaning'),
        (KITCHEN, 'Kitchen'),
        (OTHERS, 'Others'),
    )

    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

    ACTIVATION_STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    NEW = 'New'
    LIKE_NEW = 'Like New'
    VERY_GOOD = 'Very Good'
    GOOD = 'Good'
    USABLE = 'Usable'

    CONDITION_CHOICES = (
        (NEW, 'New'),
        (LIKE_NEW, 'Like New'),
        (VERY_GOOD, 'Very Good'),
        (GOOD, 'Good'),
        (USABLE, 'Usable'),
    )

    HOME = 'Home'
    SHED = 'Shed'

    LOCATION = (
        (HOME, 'Home'),
        (SHED, 'Shed'),
    )


    tool_name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'autofocus': 'autofocus','class':'form-control','style':'width:100%;'}))
    condition = forms.ChoiceField(widget=forms.RadioSelect, choices=CONDITION_CHOICES)
    location = forms.ChoiceField(widget=forms.RadioSelect,choices=LOCATION)
    status = forms.ChoiceField(widget=forms.RadioSelect, choices=ACTIVATION_STATUS_CHOICES, initial=ACTIVE)
    category = forms.ChoiceField(widget=forms.RadioSelect, choices=CATEGORY_CHOICES)
    special_instruction = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), required=False)
    image = forms.FileField(label='Select the tool image')

    def clean_image(self):
        image = self.cleaned_data['image']
        if image:
            file_type = image.content_type.split('/')[0]
            print(file_type)
            if len(image.name.split('.')) == 1:
                raise forms.ValidationError("File type is not supported.")
            if image._size > 4*1024*1024:
                raise forms.ValidationError("Image too large.Maximum image size is 4MB")
            if image.name.split('.')[-1] in ['png', 'jpg']:
                return image
            else:
                raise forms.ValidationError("Only '.png' and '.jpg' files are allowed.")




    def clean_tool_name(self):
        text = self.cleaned_data['tool_name']
        if any(char.isdigit()for char in text):
            raise forms.ValidationError("Tool name should not contain numbers.")



class ShedCreation(forms.Form):
    name = forms.CharField(max_length=30, label='Shed name',widget=forms.TextInput(attrs={'autofocus': 'autofocus','class':'form-control','style':'width:100%;'}))
    address = forms.CharField(max_length=20, label='Shed address',widget=forms.TextInput(attrs={'autofocus': 'autofocus','class':'form-control','style':'width:100%;'}))


class UpdatePersonalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

class UpdatePersonalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

class UpdatePersonalInfoForm2(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]

class UpdateUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["address"]

class UpdateUserProfileForm2(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["gender"]

class UpdateToolsForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ["id","tool_name","status","location","condition","special_instruction","category","image"]


    def clean(self):
        status = self.cleaned_data['status']
        location = self.cleaned_data['location']
        if location == "Shed" and status=="Inactive":
            raise forms.ValidationError({'status': ["Tool cannot be set deactive when it is in the Shed."]})

class UpdatePasswordForm(forms.Form):
    password_1 = forms.CharField(widget=forms.PasswordInput())
    password_2 = forms.CharField(widget=forms.PasswordInput())


class TransactionCompletionForm(forms.Form):

    NEW = 'New'
    LIKE_NEW = 'Like New'
    VERY_GOOD = 'Very Good'
    GOOD = 'Good'
    USABLE = 'Usable'

    CONDITION_CHOICES = (
        (NEW, 'New'),
        (LIKE_NEW, 'Like New'),
        (VERY_GOOD, 'Very Good'),
        (GOOD, 'Good'),
        (USABLE, 'Usable'),
    )

    condition = forms.ChoiceField(widget=forms.RadioSelect, choices=CONDITION_CHOICES, required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}),max_length=256, required=False)
    date = forms.CharField(widget=forms.TextInput(attrs={'id':'to','class':'form-control'}), required=False)

class UpdateShareZoneForm2(forms.Form):
    zipcode = forms.CharField(max_length=5,widget=forms.TextInput(attrs={'class':'form-control','style':'width:100%'}))

class UpdateShareZoneForm1(forms.ModelForm):
    class Meta:
        model = Shed
        fields = ["zipcode"]