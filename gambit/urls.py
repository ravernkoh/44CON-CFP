from django.conf.urls import include, url, handler400, handler403, handler404, handler500
from django.contrib import admin

from . import views

app_name = 'gambit'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.IndexView.as_view(), name='index'),
]

handler400 = views.BadRequestView.as_view()
handler403 = views.PermissionDeniedView.as_view()
handler404 = views.PageNotFoundView.as_view()
handler500 = views.ServerErrorView.as_view()
