from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path(
        'logout/',
        views.LogoutView.as_view(template_name='logged_out.html'),
        name='logout',
    ),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
