"""URL configuration for gym_app project."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('apps.authentication.urls')),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.catalog.urls')),
    path('api/', include('apps.splits.urls')),
    path('api/', include('apps.routines.urls')),
    path('api/', include('apps.workouts.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
