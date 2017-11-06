from django.views import generic
from django.contrib.auth import login
from gambit.forms import SignUpForm
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from gambit.tokens import account_activation_token
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site

class IndexView(generic.TemplateView):
    template_name = 'gambit/index.html'


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'gambit/profile.html'
    login_url = 'login'


class ErrorView(generic.TemplateView):
    template_name = 'gambit/error.html'

    def __init__(self):
        self.error_value = 0
        self.error_type = 'Error'

    def get_context_data(self, **kwargs):
        context = super(ErrorView, self).get_context_data(**kwargs)
        context['error_value'] = "{0!s}".format(self.error_value)
        context['error_type'] = self.error_type
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(ErrorView, self).render_to_response(context, **response_kwargs)
        response.status_code = self.error_value
        return response


class BadRequestView(ErrorView):
    def __init__(self):
        self.error_value = 400
        self.error_type = 'Bad Request'


class PermissionDeniedView(ErrorView):
    def __init__(self):
        self.error_value = 403
        self.error_type = 'Permission Denied'


class PageNotFoundView(ErrorView):
    def __init__(self):
        self.error_value = 404
        self.error_type = 'Page Not Found'


class ServerErrorView(ErrorView):
    def __init__(self):
        self.error_value = 500
        self.error_type = 'Server Error'


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.name = form.cleaned_data.get('name')
            user.profile.country = form.cleaned_data.get('country')
            user.profile.affiliation = form.cleaned_data.get('affiliation')
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your 44CON CFP account'
            message = render_to_string('gambit/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'gambit/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'gambit/account_activation_invalid.html')


def account_activation_sent(request):
    return render(request, 'gambit/account_activation_sent.html')
