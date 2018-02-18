from django.conf import settings
from django.contrib import admin
from django.urls import reverse_lazy
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


from . import views
from .forms import LoginForm, ResetUserPasswordForm, SetUserPasswordForm, ChangeUserPasswordForm


app_name = "gambit"
uuid_regex = "[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[89aAbB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}"
uidb64_regex = "[0-9A-Za-z_\-]+"
token_regex = "[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}"

urlpatterns = [
    url(r"^$", views.Home.as_view(), name="home",),
    url(r"^admin/", admin.site.urls,),
    url(r'^hijack/', include('hijack.urls', namespace='hijack')),
    url(r"^profile/$", views.ViewProfile.as_view(), name="profile",),
    url(r"^update_profile/$", views.UpdateProfile.as_view(), name="update_profile",),
    url(r"^signup/$", views.signup, name="signup",),
    url(r"^help/$", views.Help.as_view(), name="help",),
    url(r"^account_activation_sent/$", views.account_activation_sent, name="account_activation_sent",),
    url(r"^submit/$", views.submit_form_upload, name="submit",),
    url(r"^submissions/$", views.ListSubmission.as_view(), name="list_submissions",),

    url(r"^password_change/$",
        auth_views.PasswordChangeView.as_view(
            template_name="gambit/password_change.html",
            form_class=ChangeUserPasswordForm,
            success_url=reverse_lazy("password_change_done"),
        ),
        name="password_change",
    ),

    url(r"^password_change_done/$",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="gambit/password_change_done.html",
        ),
        name="password_change_done",
    ),

    url(fr"^submission/(?P<uuid>{uuid_regex!s})/$",
        views.ViewSubmission.as_view(),
        name="submission",
    ),

    url(fr"^update_submission/(?P<pk>{uuid_regex!s})/$",
        views.UpdateSubmission.as_view(),
        name="update_submission",
    ),

    url(fr"^new_review/(?P<uuid>{uuid_regex!s})/$",
        views.CreateReview.as_view(),
        name="new_review",
    ),

    url(fr"^update_review/(?P<pk>{uuid_regex!s})/$",
        views.UpdateReview.as_view(),
        name="update_review",
    ),

    url(r"^login/$",
        auth_views.LoginView.as_view(
            template_name="gambit/login.html",
            redirect_authenticated_user=True,
            authentication_form=LoginForm,
        ),
        name ="login",
    ),

    url(r"^logout/$",
        auth_views.LogoutView.as_view(next_page="home"),
        name ="logout"
    ),

    url(fr"^activate/(?P<uidb64>{uidb64_regex!s})/(?P<token>{token_regex!s})/$",
        views.activate,
        name="activate",
    ),

    url(r"^password_reset/$",
        auth_views.PasswordResetView.as_view(
            form_class=ResetUserPasswordForm,
            template_name="gambit/password_reset_form.html",
            email_template_name="gambit/password_reset_email.html",
            subject_template_name="gambit/password_reset_subject.txt",
        ),
        name="password_reset",
    ),

    url(r"^password_reset/done/$",
        auth_views.PasswordResetDoneView.as_view(
            template_name="gambit/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    url(fr"^reset/(?P<uidb64>{uidb64_regex!s})/(?P<token>{token_regex!s})/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="gambit/password_reset_confirm.html",
            form_class=SetUserPasswordForm,
        ),
        name="password_reset_confirm",
    ),

    url(r"^reset/done/$",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="gambit/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]

handler400 = views.BadRequest.as_view()
handler403 = views.PermissionDenied.as_view()
handler404 = views.PageNotFound.as_view()
handler500 = views.ServerError.as_view()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
