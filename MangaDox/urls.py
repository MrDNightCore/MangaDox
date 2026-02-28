from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('manga.urls')),
]

# Global CSRF failure handler (routes 403 errors to our custom view)
handler403 = 'users.views.csrf_failure'

# Serve media files (uploaded covers, chapter images, etc.)
# In production on Render this still helps when files exist on disk (before redeploy).
# For persistent media storage, configure S3 via USE_S3=True in environment variables.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
