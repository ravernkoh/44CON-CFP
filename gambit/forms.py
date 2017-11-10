from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from .models import Submission


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required - Input a valid email address.')
    name = forms.CharField(max_length=128, required=True, help_text='Required - Preferably your full name.')
    country = forms.CharField(max_length=48, required=True, help_text='Required - Your country of residence.')
    affiliation = forms.CharField(max_length=32, required=False, help_text='Optional - Your employer or place of study.')

    def clean(self):
        email = self.cleaned_data['email']
        username = self.cleaned_data['username']

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Email addresses has already been used.'))

        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Username already exists.'))


    class Meta:
        model = User
        fields = ['username', 'name', 'country', 'affiliation', 'email', 'password1', 'password2']


class SubmitForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(SubmitForm, self).clean()
        abstract = cleaned_data.get('abstract')
        file = cleaned_data.get('file')

        if not abstract and not file:
            raise forms.ValidationError(_('Must include an abstract or upload a document.'))
        else:
            pass

    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            content_type = file.content_type
            if content_type in settings.CONTENT_TYPES:
                if file._size > settings.MAX_UPLOAD_SIZE:
                    raise forms.ValidationError(_('Submitted file is too large. Please limit uploads to 5MiB.'))
            else:
                raise forms.ValidationError(_('File type is not allowed.'))
            return file
        else:
            pass


    class Meta:
        model = Submission
        fields = ['title', 'abstract', 'authors', 'contact_email', 'conflicts', 'file', 'user']
        exclude = ['user']
        help_texts = {
            'title': 'Required - Can be a working title',
            'abstract': 'Optional but preferred - Can be a brief outline (supported by an uploaded document) or detailed overview of your submission',
            'authors': 'Optional - Names of additional authors',
            'contact_email': 'Required - Email address that 44CON Speaker Ops should use for contact',
            'conflicts': 'Optional - Names of any Programme Committee members who have conflicts of interest with this submission. This includes past advisors and students, people who share the same affiliation (employer or place of study), and any recent coauthors or collaborators.',
            'file': 'File size limit: 5MiB'
        }
        widgets = {
            'abstract': forms.Textarea(attrs={'rows': 8, 'cols': 60}),
            'authors': forms.Textarea(attrs={'rows': 4, 'cols': 60}),
            'conflicts': forms.Textarea(attrs={'rows': 4, 'cols': 60})
        }
