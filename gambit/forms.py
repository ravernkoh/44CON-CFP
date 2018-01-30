from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.fields.files import FieldFile
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm

from .models import Submission, SubmissionReview, Profile
from .blacklist import reserved_usernames


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=254,
                                widget=forms.TextInput(attrs={
                                    'type': 'text',
                                    'class': 'form-control',
                                    'name': 'username',
                                    'autofocus': 'autofocus',
                                }))
    password = forms.CharField(label="Password",
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'form-control',
                                    'name': 'password',
                                }))


class FrontPageLoginForm(LoginForm):
    username = forms.CharField(label="Username", max_length=254,
                                widget=forms.TextInput(attrs={
                                    'type': 'text',
                                    'class': 'form-control',
                                    'name': 'username',
                                }))


class ChangeUserPasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Old password",
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'form-control',
                                    'name': 'old_password',
                                    'autofocus': 'autofocus',
                                }))
    new_password1 = forms.CharField(label="New password",
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'form-control',
                                    'name': 'password1',
                                }))
    new_password2 = forms.CharField(label="New password confirmation",
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'form-control',
                                    'name': 'password2',
                                }))


class ResetUserPasswordForm(PasswordResetForm):
    email = forms.EmailField(label="Email Address", max_length=254,
                                widget=forms.EmailInput(attrs={
                                    'type': 'email',
                                    'class': 'form-control',
                                    'name': 'email',
                                    'autofocus': 'autofocus',
                                }))


class SetUserPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label="New password",
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'form-control',
                                    'name': 'password1',
                                    'autofocus': 'autofocus',
                                }))
    new_password2 = forms.CharField(label="New password confirmation",
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'form-control',
                                    'name': 'password2',
                                }))


class SignUpForm(UserCreationForm):
    username = forms.CharField(label="<strong>Username</strong>", max_length=254,
                                widget=forms.TextInput(attrs={
                                    'type': 'text',
                                    'class': 'form-control',
                                    'name': 'username',
                                    'placeholder': '150 characters or fewer. Alphanumeric characters and @/./+/-/_ only',
                                    'autofocus': 'autofocus',
                                    }))
    password1 = forms.CharField(label="<strong>Password</strong>",
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'form-control',
                                    'name': 'password1',
                                    'placeholder': 'Password must contain at least 12 characters',
                                }))
    password2 = forms.CharField(label="<strong>Password Confirmation</strong>",
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'form-control',
                                    'name': 'password2',
                                    'placeholder': 'Enter the same password as before for verification',
                                }))
    email = forms.EmailField(label="<strong>Email</strong>", max_length=254,
                                widget=forms.TextInput(attrs={
                                    'type': 'email',
                                    'class': 'form-control',
                                    'placeholder': 'A valid email address',
                                }))
    name = forms.CharField(label="<strong>Name</strong>", max_length=128, required=True,
                            widget=forms.TextInput(attrs={
                                'type': 'text',
                                'class': 'form-control',
                                'placeholder': 'Preferably your full name',
                            }))
    country = forms.CharField(label="<strong>Country</strong>", max_length=48, required=True,
                            widget=forms.TextInput(attrs={
                                'type': 'text',
                                'class': 'form-control',
                                'placeholder': 'Your country of residence',
                            }))
    affiliation = forms.CharField(label="Affiliation", max_length=32, required=False,
                            widget=forms.TextInput(attrs={
                                'type': 'text',
                                'class': 'form-control',
                                'placeholder': 'Your employer or place of study',
                            }))

    def clean(self):
        email = self.cleaned_data["email"]
        username = self.cleaned_data["username"]

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email address has already been used."))

        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Username already exists."))

        if username in reserved_usernames:
            raise forms.ValidationError(_("This username is restricted or otherwise unavailable. Please pick another."))


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


class UpdateProfileForm(forms.ModelForm):
    email = forms.EmailField(max_length=254,
                                widget=forms.TextInput(attrs={
                                    'type': 'email',
                                    'class': 'form-control',
                                }))


    class Meta:
        """Define object, fields, and styling"""
        model = Profile
        fields = [
            'name',
            'country',
            'affiliation',
            'email',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'autofocus': 'autofocus',
            }),
            'country': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
            }),
            'affiliation': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
            }),
        }


class SubmitForm(forms.ModelForm):
    """Form used for both submitting and editing"""
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
                    raise forms.ValidationError(_("Submitted file is too large. Please limit uploads to 50MiB."))
            else:
                raise forms.ValidationError(_("File type is not allowed (Allowed types: pdf, doc/x, ppt/s, zip)."))
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
        conflicts_placeholder = (
            'If you have any conflicts of interest with the panel - i.e. you are aware of having worked with, co-authored, or co-presented with panel'
            'members, please list their names here. It helps us ensure a fair process is followed.'
        )
        help_texts = {
            'file': (
                'If you have any specific requirements, constraints, supporting content, or just pictures of your cat then please upload them using '
                'this form.<br>If you have multiple files to upload, the form will accept a zip file.<br>'
                'File size limit: <span class=\'text-danger\'>50MiB</span>. Permitted data types: pdf, doc/x, ppt/s, zip'
            ),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Can be a working title',
                'autofocus': 'autofocus',
            }),
            'abstract': forms.Textarea(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': abstract_placeholder,
            }),
            'authors': forms.Textarea(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Names of additional authors',
            }),
            'contact_email': forms.EmailInput(attrs={
                'type': 'email',
                'class': 'form-control',
                'placeholder': 'Primary email address that 44CON Speaker Ops should use for contact',
            }),
            'conflicts': forms.Textarea(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': conflicts_placeholder,
            }),
        }
        labels = {
            'title': '<strong>Title</strong>',
            'contact_email': '<strong>Contact Email</strong>',
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
            'comments': (
                'Please be reasonable and courteous when reviewing (to the best of your ability). Due to the UK\'s Data Protection Laws, it is '
                'distinctly possible that someone could ask for a copy of the review comments on their submission(s). Just bear that in mind when commenting.'
            ),
        }
        widgets = {
            'expertise_score': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'autofocus': 'autofocus',
            }),
            'submission_score': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'min': 1,
                'max': 5,
            }),
            'comments': forms.Textarea(attrs={
                'type': 'text',
                'class': 'form-control',
            }),
        }
