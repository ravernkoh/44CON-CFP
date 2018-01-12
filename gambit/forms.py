from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.fields.files import FieldFile
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from .models import Submission, SubmissionReview


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text="Required - Input a valid email address.")
    name = forms.CharField(max_length=128, required=True, help_text="Required - Preferably your full name.")
    country = forms.CharField(max_length=48, required=True, help_text="Required - Your country of residence.")
    affiliation = forms.CharField(max_length=32, required=False, help_text="Optional - Your employer or place of study.")

    def clean(self):
        email = self.cleaned_data["email"]
        username = self.cleaned_data["username"]

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email address has already been used."))

        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Username already exists."))


    class Meta:
        """Define the model and fields to display"""
        model = User
        fields = [
            'username',
            'name',
            'country',
            'affiliation',
            'email',
            'password1',
            'password2',
        ]


class SubmitForm(forms.ModelForm):
    """Form used for both submitting and editing"""
    def clean(self):
        cleaned_data = super(SubmitForm, self).clean()
        abstract = cleaned_data.get("abstract")
        file = cleaned_data.get("file")

    def clean_file(self):
        # Reject file if it's not a valid content type or if it's too large
        file = self.cleaned_data["file"]
        # If type(file) == FieldFile, then the file has already been uploaded during submission or a previous edit and does not need to be cleaned.
        # It will throw an AttributeError on the content_type assignment because the model does not have such a field.
        # This may happen when the user tries to change the uploaded file but a ValidationError occurs.
        # If the user then chooses not to select a different file but clicks submit to update the submission, clean_file() will attempt to process the
        # file which is actually a FieldFile causing the error described before.
        if file and not isinstance(file, FieldFile):
            content_type = file.content_type
            if content_type in settings.CONTENT_TYPES:
                if file.size > settings.MAX_UPLOAD_SIZE:
                    raise forms.ValidationError(_("Submitted file is too large. Please limit uploads to 5MiB."))
            else:
                raise forms.ValidationError(_("File type is not allowed (Allowed types: pdf, doc/x)."))
            return file


    class Meta:
        """Define object, fields, and styling"""
        model = Submission
        fields = [
            'title',
            'abstract',
            'authors',
            'contact_email',
            'conflicts',
            'file',
            'user',
        ]
        exclude = ['user',]
        abstract_placeholder = "Can be a brief outline (supported by an uploaded document) or detailed overview of your submission"
        conflicts_placeholder = "If you have any conflicts of interest with the panel - i.e. you are aware of having worked with, co-authored, or co-presented with panel members, please list their names here. It helps us ensure a fair process is followed."
        help_texts = {
            'file': 'If you have any specific requirements, constraints, supporting content, or just pictures of your cat then please upload them using \
            this form.<br>If you have multiple files to upload, the form will accept a zip file.<br>File size limit: 50MiB. Permitted data types: \
            pdf, doc/x, ppt/s, zip',
        }
        widgets = {
            'title': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Can be a working title'}),
            'abstract': forms.Textarea(attrs={'type': 'text', 'class': 'form-control', 'placeholder': abstract_placeholder}),
            'authors': forms.Textarea(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Names of additional authors'}),
            'contact_email': forms.EmailInput(attrs={'type': 'email', 'class': 'form-control', 'placeholder': 'Primary email address that 44CON Speaker Ops should use for contact'}),
            'conflicts': forms.Textarea(attrs={'type': 'text', 'class': 'form-control', 'placeholder': conflicts_placeholder}),
        }
        labels = {
            'title': 'Title *',
            'contact_email': 'Contact Email *',
        }


class SubmissionReviewForm(forms.ModelForm):
    """Form used for both creating and updating reviews"""


    class Meta:
        """Define object, fields, and styling"""
        model = SubmissionReview
        fields = [
            'expertise_score',
            'submission_score',
            'comments',
            'user',
        ]
        exclude = ['user',]
        help_texts = {
            'expertise_score': 'An approximation of your personal expertise in the field of the submission, where 1 is a complete novice and 5 is a expert',
            'submission_score': 'Your rating of the quality of this submission, where 1 is very poor and 5 is great',
            'comments': 'Please be reasonable and courteous when reviewing (to the best of your ability). Due to the UK\'s Data Protection Laws, it is \
            distinctly possible that someone could ask for a copy of the review comments on their submission(s). Just bear that in mind when commenting.',
        }
        widgets = {
            'expertise_score': forms.NumberInput(attrs={'type': 'number', 'class': 'form-control', 'min': 1, 'max': 5}),
            'submission_score': forms.NumberInput(attrs={'type': 'number', 'class': 'form-control', 'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'type': 'text', 'class': 'form-control'}),
        }
