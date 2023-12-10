from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static

import chat.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("allauth.urls")),
    path('settings/', chat.views.settings, name='settings'),
    path('chat/', include('chat.urls')),
    path('', include('chat.urls')),
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("favicon/favicon.ico")),),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
