from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static

from catalogo.views import (
    CustomAuthToken, RegisterAPIView, MeAPIView,
    ResetTokenAPIView, LogoutAPIView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalogo.urls')),
    path('api/', include('catalogo.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Endpoints de Autenticación
    re_path(r'^api/custom-token/?$', CustomAuthToken.as_view(), name='custom_auth_token'),
    re_path(r'^custom-token/?$', CustomAuthToken.as_view(), name='custom_auth_token_root'),
    re_path(r'^api/login/?$', CustomAuthToken.as_view(), name='login_token'),
    re_path(r'^login/?$', CustomAuthToken.as_view(), name='login_token_root'),

    re_path(r'^api/register/?$', RegisterAPIView.as_view(), name='register'),
    re_path(r'^register/?$', RegisterAPIView.as_view(), name='register_root'),

    re_path(r'^api/me/?$', MeAPIView.as_view(), name='me'),
    re_path(r'^me/?$', MeAPIView.as_view(), name='me_root'),

    re_path(r'^api/resettoken/?$', ResetTokenAPIView.as_view(), name='reset_token'),
    re_path(r'^resettoken/?$', ResetTokenAPIView.as_view(), name='reset_token_root'),
    re_path(r'^api/reset-token/?$', ResetTokenAPIView.as_view(), name='reset_token_hyphen'),
    re_path(r'^reset-token/?$', ResetTokenAPIView.as_view(), name='reset_token_hyphen_root'),

    re_path(r'^api/logout/?$', LogoutAPIView.as_view(), name='logout'),
    re_path(r'^logout/?$', LogoutAPIView.as_view(), name='logout_root'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
