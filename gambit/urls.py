from django.conf import settings
from django.contrib import admin
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import reverse_lazy, path, re_path
from django.contrib.auth import views as auth_views


from . import views
from .forms import LoginForm, ResetUserPasswordForm, SetUserPasswordForm, ChangeUserPasswordForm


app_name = "gambit"
uidb64_regex = "[0-9A-Za-z_\-]+"
token_regex = "[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}"

urlpatterns = [
    re_path(r"^$", views.Home.as_view(), name="home",),
    path("admin/", admin.site.urls,),
    path("hijack/", include("hijack.urls", namespace="hijack")),
    path("profile/", views.ViewProfile.as_view(), name="profile",),
    path("update_profile/", views.UpdateProfile.as_view(), name="update_profile",),
    path("signup/", views.signup, name="signup",),
    path("help/", views.Help.as_view(), name="help",),
    path("account_activation_sent/", views.account_activation_sent, name="account_activation_sent",),
    path("submit/", views.submit_form_upload, name="submit",),
    path("submissions/", views.ListSubmission.as_view(), name="list_submissions",),

    path("download/submission/<uuid:pk>/",
        views.SubmissionFileView.as_view(),
        name="download_submission"
    ),

    path("password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="gambit/password_change.html",
            form_class=ChangeUserPasswordForm,
            success_url=reverse_lazy("password_change_done"),
        ),
        name="password_change",
    ),

    path("password_change_done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="gambit/password_change_done.html",
        ),
        name="password_change_done",
    ),

    path("submission/<uuid:uuid>/",
        views.ViewSubmission.as_view(),
        name="submission",
    ),

    path("update_submission/<uuid:pk>/",
        views.UpdateSubmission.as_view(),
        name="update_submission",
    ),

    path("new_review/<uuid:uuid>/",
        views.CreateReview.as_view(),
        name="new_review",
    ),

    path("update_review/<uuid:pk>/",
        views.UpdateReview.as_view(),
        name="update_review",
    ),

    path("login/",
        auth_views.LoginView.as_view(
            template_name="gambit/login.html",
            redirect_authenticated_user=True,
            authentication_form=LoginForm,
        ),
        name ="login",
    ),

    path("logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name ="logout"
    ),

    re_path(fr"^activate/(?P<uidb64>{uidb64_regex!s})/(?P<token>{token_regex!s})/$",
        views.activate,
        name="activate",
    ),

    path("password_reset/",
        auth_views.PasswordResetView.as_view(
            form_class=ResetUserPasswordForm,
            template_name="gambit/password_reset_form.html",
            email_template_name="gambit/password_reset_email.html",
            subject_template_name="gambit/password_reset_subject.txt",
        ),
        name="password_reset",
    ),

    path("password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="gambit/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    re_path(fr"^reset/(?P<uidb64>{uidb64_regex!s})/(?P<token>{token_regex!s})/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="gambit/password_reset_confirm.html",
            form_class=SetUserPasswordForm,
        ),
        name="password_reset_confirm",
    ),

    path("reset/done/",
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
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
