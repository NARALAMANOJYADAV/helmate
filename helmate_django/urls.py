from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('detection.urls')),
]

# Media files serving (uploads)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files serving (static URL)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Catch-all for other assets served from root for legacy support
# This MUST be last to avoid intercepting valid media/static paths
urlpatterns += [
    re_path(r'^(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]}),
]
