import os
import logging

import coloredlogs
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, mixins, REDIRECT_FIELD_NAME

from .tokens import account_activation_token
from .models import Submission, SubmissionReview, FrontPage, HelpPageItem
from .forms import SignUpForm, SubmitForm, SubmissionReviewForm, LoginForm


# ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
# Invoke with logger.<error_level>(<message>)
# e.g. logger.debug("This is a test message.")
# Messages which are LESS severe than the current level will be ignored
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")


class Home(generic.edit.FormMixin, generic.TemplateView):
    template_name = "gambit/home.html"
    form_class = LoginForm
    redirect_field_name = REDIRECT_FIELD_NAME

    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(Home, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return super(Home, self).form_valid(form)

    def get_success_url(self):
        return reverse('home')

    def get(self, request, *args, **kwargs):
        return super(Home, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """Return front page content"""
        context = super(Home, self).get_context_data(**kwargs)
        context["front_page_content"] = get_object_or_404(FrontPage, id=1)
        return context


class Profile(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "gambit/profile.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        """Return submissions"""
        context = super(Profile, self).get_context_data(**kwargs)
        context["submissions"] = Submission.objects.filter(user=self.request.user).order_by("submitted_on")
        return context


class ViewSubmission(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "gambit/submission_view.html"
    login_url = "login"
    model = Submission

    def get_context_data(self, **kwargs):
        """Return submission data"""
        context = super(ViewSubmission, self).get_context_data(**kwargs)
        context["submission"] = get_object_or_404(Submission, uuid=self.kwargs["uuid"])
        if context["submission"].file:
            _, tail = os.path.split(context["submission"].file.name)  # Discarding path prefix
            context["submission_file_name"] = tail
        context["reviews"] = context["submission"].get_reviews()
        context["has_reviewed"] = True if SubmissionReview.objects.filter(submission=context["submission"], user=self.request.user) else False
        if context["has_reviewed"]:
            context["review_uuid"] = SubmissionReview.objects.filter(submission=context["submission"], user=self.request.user)[0].uuid
        return context


class UpdateSubmission(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.edit.UpdateView):
    model = Submission
    form_class = SubmitForm
    template_name_suffix = "_update"
    login_url = "login"
    redirect_field_name = "home"

    # Is model owned by editor?
    def test_func(self):
        return Submission.objects.get(uuid=self.kwargs.get('pk')).user.id == self.request.user.id

    def get_success_url(self):
        return reverse('submission', args=[self.object.uuid])


class ListSubmission(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.TemplateView):
    template_name = "gambit/submission_list.html"
    login_url = "login"
    redirect_field_name = "home"

    # Is the logged in user an admin or a member of the PC?
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name="Programme Committee").exists()

    def get_context_data(self, **kwargs):
        """Return all submissions"""
        context = super(ListSubmission, self).get_context_data(**kwargs)
        context["submissions"] = Submission.objects.all().order_by("submitted_on")
        return context


class CreateReview(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.edit.CreateView):
    model = SubmissionReview
    form_class = SubmissionReviewForm
    template_name_suffix = "_create"
    login_url = "login"
    redirect_field_name = "home"

    # Is the logged in user an admin or a member of the PC?
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name="Programme Committee").exists()

    def get_context_data(self, **kwargs):
        """Return submission data"""
        context = super(CreateReview, self).get_context_data(**kwargs)
        context["submission"] = get_object_or_404(Submission, uuid=self.kwargs["uuid"])
        if context["submission"].file:
            _, tail = os.path.split(context["submission"].file.name)  # Discarding path prefix
            context["submission_file_name"] = tail
        return context

    def form_valid(self, form):
        review = form.save(commit=False)
        review.submission = get_object_or_404(Submission, uuid=self.kwargs["uuid"])
        review.user = self.request.user
        return super(CreateReview, self).form_valid(form)

    def get_success_url(self):
        return reverse('submission', args=[self.kwargs["uuid"]])


class UpdateReview(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.edit.UpdateView):
    model = SubmissionReview
    form_class = SubmissionReviewForm
    template_name_suffix = "_update"
    login_url = "login"
    redirect_field_name = "home"

    # Is the logged in user an admin or a member of the PC?
    def test_func(self):
        return (self.request.user.is_superuser or \
                self.request.user.groups.filter(name="Programme Committee").exists()) and \
                SubmissionReview.objects.get(uuid=self.kwargs.get('pk')).user.id == self.request.user.id

    def get_context_data(self, **kwargs):
        """Return submission data"""
        context = super(UpdateReview, self).get_context_data(**kwargs)
        context["submission"] = get_object_or_404(Submission, uuid=self.object.submission.uuid)
        if context["submission"].file:
            _, tail = os.path.split(context["submission"].file.name)  # Discarding path prefix
            context["submission_file_name"] = tail
        return context

    def get_success_url(self):
        return reverse('submission', args=[self.object.submission.uuid])


class Help(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "gambit/help.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        """Return help page content"""
        context = super(Help, self).get_context_data(**kwargs)
        context["help_page_lead"] = HelpPageItem.objects.filter(lead=True)[0]
        context["help_page_items"] = HelpPageItem.objects.exclude(lead=True).order_by("id")
        return context


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.name = form.cleaned_data.get("name")
            user.profile.country = form.cleaned_data.get("country")
            user.profile.affiliation = form.cleaned_data.get("affiliation")
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = "[44CON] Activate your 44CON CFP account"
            message = render_to_string("gambit/account_activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect("account_activation_sent")
    else:
        form = SignUpForm()
    return render(request, "gambit/signup.html", {"form": form})

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
        return redirect("home")
    else:
        return render(request, "gambit/account_activation_invalid.html")

def account_activation_sent(request):
    return render(request, "gambit/account_activation_sent.html")

@login_required(login_url="login")
def submit_form_upload(request):
    # Prevent submissions after deadline has passed
    if timezone.now() <= FrontPage.objects.get(id=1).submission_deadline:
        if request.method == "POST":
            form = SubmitForm(request.POST, request.FILES)
            if form.is_valid():
                # Associates the submission with the logged in user. There may be a more "elegant" way to achieve this but this works and is robust.
                # Submissions can only be made by logged in users which ensures the presence of the user model in the request.
                f = form.save(commit=False)
                f.user = request.user
                f.save()
                f.refresh_from_db()
                return redirect(reverse("submission", args=[f.uuid]))
        else:
            form = SubmitForm()
        return render(request, "gambit/submit.html", {
            "form": form
        })
    else:
        return render(request, "gambit/submit.html", {
            "deadline_passed": True
        })


class GenericError(generic.TemplateView):
    template_name = "gambit/error.html"

    def __init__(self):
        self.error_value = 0
        self.error_type = "Error"

    def get_context_data(self, **kwargs):
        context = super(GenericError, self).get_context_data(**kwargs)
        context["error_value"] = f"{self.error_value!s}"
        context["error_type"] = self.error_type
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(GenericError, self).render_to_response(context, **response_kwargs)
        response.status_code = self.error_value
        return response


class BadRequest(GenericError):
    def __init__(self):
        self.error_value = 400
        self.error_type = "Bad Request"


class PermissionDenied(GenericError):
    def __init__(self):
        self.error_value = 403
        self.error_type = "Permission Denied"


class PageNotFound(GenericError):
    def __init__(self):
        self.error_value = 404
        self.error_type = "Page Not Found"


class ServerError(GenericError):
    def __init__(self):
        self.error_value = 500
        self.error_type = "Server Error"
