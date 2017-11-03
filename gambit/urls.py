from django.conf.urls import include, url, handler400, handler403, handler404, handler500
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views

app_name = 'gambit'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^login/$', auth_views.login, {'template_name': 'gambit/login.html'}, name ='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'index'}, name ='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'gambit/password_reset_form.html', 'email_template_name': 'gambit/password_reset_email.html', 'subject_template_name': 'gambit/password_reset_subject.txt'}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name': 'gambit/password_reset_done.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'template_name': 'gambit/password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'gambit/password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]

handler400 = views.BadRequestView.as_view()
handler403 = views.PermissionDeniedView.as_view()
handler404 = views.PageNotFoundView.as_view()
handler500 = views.ServerErrorView.as_view()
