from datetime import datetime

from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django_downloadview import ObjectDownloadView
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, mixins, REDIRECT_FIELD_NAME
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .tokens import account_activation_token
from .forms import SignUpForm, SubmitForm, SubmissionReviewForm, FrontPageLoginForm, UpdateProfileForm
from .models import (Submission, SubmissionReview, FrontPage, SubmissionDeadline, RegistrationStatus, HelpPageItem,
    Profile)


class Home(generic.edit.FormMixin, generic.TemplateView):
    template_name = "gambit/home.html"
    form_class = FrontPageLoginForm
    redirect_field_name = REDIRECT_FIELD_NAME

    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(Home, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        session = self.request.session
        if session.test_cookie_worked():
            session.delete_test_cookie()
        else:
            session.delete_test_cookie()
        return super(Home, self).form_valid(form)

    def get_success_url(self):
        return reverse("home")

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """Return front page content"""
        context = super(Home, self).get_context_data(**kwargs)
        try:
            front_page = FrontPage.objects.first()
            context["front_page"] = front_page
        except FrontPage.DoesNotExist:
            context["front_page"] = None
        return context


class ViewProfile(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "gambit/profile_view.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        """Return submissions"""
        context = super(ViewProfile, self).get_context_data(**kwargs)
        user = self.request.user
        profile = user.profile
        context["submissions"] = profile.get_submissions()
        is_pc = user.groups.filter(name="Programme Committee").exists()
        if is_pc:
            context["reviews"] = profile.get_reviews()
        return context


class UpdateProfile(SuccessMessageMixin, mixins.LoginRequiredMixin, generic.edit.UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name_suffix = "_update"
    login_required = "login"
    success_message = "Profile updated successfully"

    def get_context_data(self, **kwargs):
        context = super(UpdateProfile, self).get_context_data(**kwargs)
        data = {
            'name': self.object.name,
            'country': self.object.country,
            'affiliation': self.object.affiliation,
            'email': self.object.user.email,
        }
        context['form'] = self.form_class(initial=data)
        return context

    def form_valid(self, form):
        user = self.object.user
        user.email = form.cleaned_data['email']
        user.save()
        return super(UpdateProfile, self).form_valid(form)

    def get_object(self):
        user = self.request.user
        profile = user.profile
        return profile

    def get_success_url(self):
        return reverse("profile")


class ViewSubmission(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.TemplateView):
    model = Submission
    template_name = "gambit/submission_view.html"
    login_url = "login"
    redirect_field_name = "home"

    def test_func(self):
        user = self.request.user
        uuid = self.kwargs.get('uuid')  # from URL <uuid>
        submission = Submission.objects.get(uuid=uuid)
        submission_user_id = submission.user.id
        is_su = user.is_superuser
        is_pc = user.groups.filter(name="Programme Committee").exists()
        owns_submission = submission_user_id == user.id
        return is_su or is_pc or owns_submission

    def get_context_data(self, **kwargs):
        """Return submission data"""
        context = super(ViewSubmission, self).get_context_data(**kwargs)
        uuid = self.kwargs["uuid"]
        submission = get_object_or_404(Submission, uuid=uuid)
        user = self.request.user
        context["submission"] = submission
        context["submission_file_name"] = submission.get_file_name()
        context["reviews"] = submission.get_reviews()
        context["related_submissions"] = submission.get_related_submissions()
        # If submission older than 3 months (typically longer than the period the CFP is open), deny editing
        # Prevents modification of submissions from previous years
        submission_date = submission.submitted_on.date()
        context["can_edit"] = (datetime.now().date() - submission_date).days < 90
        has_reviewed = SubmissionReview.objects.filter(submission=submission, user=user).exists()
        context["has_reviewed"] = has_reviewed
        if context["has_reviewed"]:
            review = SubmissionReview.objects.filter(submission=submission, user=user).first()
            # Return UUID for review edit button URL
            context["review_uuid"] = review.uuid
        return context


class UpdateSubmission(SuccessMessageMixin, mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.edit.UpdateView):
    model = Submission
    form_class = SubmitForm
    template_name_suffix = "_update"
    login_url = "login"
    redirect_field_name = "home"
    success_message = "Submission updated successfully"

    # Is model owned by editor?
    # Is the submission over 3 months old? If so, prevent edits.
    def test_func(self):
        user = self.request.user
        uuid = self.kwargs.get('pk')
        submission = Submission.objects.get(uuid=uuid)
        submission_user_id = submission.user.id
        submission_date = submission.submitted_on.date()
        owns_submission = submission_user_id == user.id
        can_edit = (datetime.now().date() - submission_date).days < 90
        return owns_submission and can_edit

    def get_success_url(self):
        uuid = self.object.uuid
        return reverse("submission", args=[uuid])


class SubmissionFileView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, ObjectDownloadView):
    login_url = "login"
    redirect_field_name = "home"
    attachment = False  # Display files inline if possible

    def __init__(self):
        self.model = Submission

    def test_func(self):
        user = self.request.user
        uuid = self.kwargs.get('pk')
        submission = Submission.objects.get(uuid=uuid)
        submission_user_id = submission.user.id
        is_su = user.is_superuser
        is_pc = user.groups.filter(name="Programme Committee").exists()
        owns_submission = submission_user_id == user.id
        return is_su or is_pc or owns_submission


class ListSubmission(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.TemplateView):
    template_name = "gambit/submission_list.html"
    login_url = "login"
    redirect_field_name = "home"

    # Is the logged in user an admin or a member of the PC?
    def test_func(self):
        user = self.request.user
        is_su = user.is_superuser
        is_pc = user.groups.filter(name="Programme Committee").exists()
        return is_su or is_pc

    def get_context_data(self, **kwargs):
        """Return all submissions"""
        context = super(ListSubmission, self).get_context_data(**kwargs)
        user = self.request.user
        submissions = Submission.objects.all().values('uuid', 'user__profile__name', 'title', 'review_count', 'average_score', 'user__profile__country', 'submitted_on')
        context["submissions"] = submissions
        has_reviewed_list = SubmissionReview.objects.filter(user=user).values_list('submission', flat=True)
        context["reviewed"] = has_reviewed_list
        return context


class CreateReview(SuccessMessageMixin, mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.edit.CreateView):
    model = SubmissionReview
    form_class = SubmissionReviewForm
    template_name_suffix = "_create_or_update"
    login_url = "login"
    redirect_field_name = "home"
    success_message = "Review has been added"

    # Is the logged in user an admin or a member of the PC?
    # Is there an existing review from this user for this submission?
    def test_func(self):
        user = self.request.user
        uuid = self.kwargs.get('uuid')
        submission = Submission.objects.get(uuid=uuid)
        submission_user_id = submission.user.id
        is_su = user.is_superuser
        is_pc = user.groups.filter(name="Programme Committee").exists()
        has_reviewed = submission.has_reviewed(user.id)
        return is_su or is_pc and not has_reviewed

    def get_context_data(self, **kwargs):
        """Return submission data"""
        context = super(CreateReview, self).get_context_data(**kwargs)
        uuid = self.kwargs["uuid"]
        submission = get_object_or_404(Submission, uuid=uuid)
        context["submission"] = submission
        context["submission_file_name"] = submission.get_file_name()
        return context

    def form_valid(self, form):
        review = form.save(commit=False)
        uuid = self.kwargs["uuid"]
        review.submission = get_object_or_404(Submission, uuid=uuid)
        review.user = self.request.user
        return super(CreateReview, self).form_valid(form)

    def get_success_url(self):
        uuid = self.kwargs["uuid"]
        return reverse("submission", args=[uuid])


class UpdateReview(SuccessMessageMixin, mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.edit.UpdateView):
    model = SubmissionReview
    form_class = SubmissionReviewForm
    template_name_suffix = "_create_or_update"
    login_url = "login"
    redirect_field_name = "home"
    success_message = "Review has been updated"

    # Is the logged in user an admin or a member of the PC?
    def test_func(self):
        user = self.request.user
        uuid = self.kwargs.get('pk')
        review = SubmissionReview.objects.get(uuid=uuid)
        review_id = review.user.id
        is_su = user.is_superuser
        is_pc = user.groups.filter(name="Programme Committee").exists()
        owns_review = review == user.id
        return is_su or is_pc or owns_review

    def get_context_data(self, **kwargs):
        """Return submission data"""
        context = super(UpdateReview, self).get_context_data(**kwargs)
        uuid = self.object.submission_id
        submission = get_object_or_404(Submission, uuid=uuid)
        context["submission"] = submission
        context["submission_file_name"] = submission.get_file_name()
        return context

    def get_success_url(self):
        uuid = self.object.submission.uuid
        return reverse("submission", args=[uuid])


class Help(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "gambit/help.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        """Return help page content"""
        context = super(Help, self).get_context_data(**kwargs)
        help_page_items = HelpPageItem.objects.all()
        context["help_page_items"] = help_page_items
        return context


def signup(request):
    registration_status = RegistrationStatus.objects.first()
    if not registration_status.disabled:
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
                message = render_to_string("gambit/account_activation_email.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                        "token": account_activation_token.make_token(user),
                    }
                )
                user.email_user(subject, message)
                return redirect("account_activation_sent")
        else:
            form = SignUpForm()
        return render(request, "gambit/signup.html",
            {
                "form": form,
            }
        )
    else:
        return render(request, "gambit/signup.html",
            {
                "registration_disabled": True,
            }
        )

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
    try:
        deadline = SubmissionDeadline.objects.first()
        open_date = deadline.open_date
        close_date = deadline.close_date
    except AttributeError as e:
        raise SystemExit(f"No submission deadline has been added!\n{e!s}")
    
    user = request.user
    user_is_su = user.is_superuser
    current_time = timezone.now()
    
    if (current_time >= open_date and current_time <= close_date) or user_is_su:
        if request.method == "POST":
            form = SubmitForm(request.POST, request.FILES)
            if form.is_valid():
                # Associates the submission with the logged in user. There may be a more "elegant" way to achieve this
                # but this works and is robust. Submissions can only be made by logged in users which ensures the
                # presence of the user model in the request.
                f = form.save(commit=False)
                f.user = request.user
                f.save()
                f.refresh_from_db()
                messages.success(request, "Submission added successfully")
                return redirect(reverse("submission", args=[f.uuid]))
        else:
            form = SubmitForm()
        return render(request, "gambit/submit.html",
            {
                "form": form,
            }
        )
    else:
        return render(request, "gambit/submit.html",
            {
                "deadline_passed": True,
            }
        )


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


def csrf_failure(request, reason="CSRF Failure"):
    current_site = get_current_site(request)
    return render_to_response("gambit/csrf_error.html",
        {
            'error_value': 403,
            'error_type': 'CSRF Failure',
            'domain': current_site.domain
        }
    )
