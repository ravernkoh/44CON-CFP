from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import url

from . import views


app_name = "gambit"

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^$", views.IndexView.as_view(), name="index"),
    url(r"^profile/$", views.ProfileView.as_view(), name="profile"),
    url(r"^submission/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[89aAbB][a-fA-F0-9]{3}-[a-fA-F0-9]{12})/$",
        views.SubmissionView.as_view(), name="submission"),
    url(r"^submit/$", views.submit_form_upload, name="submit"),
    url(r"^submissions/$", views.AllSubmissionsView.as_view(), name="all_submissions"),
    url(r"^help/$", views.HelpView.as_view(), name="help"),
    url(r"^login/$", auth_views.login, {"template_name": "gambit/login.html", "redirect_authenticated_user": True,},
        name ="login"),
    url(r"^logout/$", auth_views.logout, {"next_page": "index"}, name ="logout"),
    url(r"^signup/$", views.signup, name="signup"),
    url(r"^password_reset/$", auth_views.password_reset, {"template_name": "gambit/password_reset_form.html",
        "email_template_name": "gambit/password_reset_email.html",
        "subject_template_name": "gambit/password_reset_subject.txt"}, name="password_reset"),
    url(r"^password_reset/done/$", auth_views.password_reset_done,
        {"template_name": "gambit/password_reset_done.html"}, name="password_reset_done"),
    url(r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        auth_views.password_reset_confirm, {"template_name": "gambit/password_reset_confirm.html"},
        name="password_reset_confirm"),
    url(r"^reset/done/$", auth_views.password_reset_complete, {"template_name": "gambit/password_reset_complete.html"},
        name="password_reset_complete"),
    url(r"^account_activation_sent/$", views.account_activation_sent, name="account_activation_sent"),
    url(r"^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$", views.activate,
        name="activate"),
]

handler400 = views.BadRequestView.as_view()
handler403 = views.PermissionDeniedView.as_view()
handler404 = views.PageNotFoundView.as_view()
handler500 = views.ServerErrorView.as_view()

# Handle requests for styles if developing locally without a web server proxy
if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
