from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from tattoo_text_generator import settings

# Define Swagger schema information
schema_view = get_schema_view(
    openapi.Info(
        title=settings.SWAGGER_SETTINGS['TITLE'],
        default_version=settings.SWAGGER_SETTINGS['VERSION'],
        description=settings.SWAGGER_SETTINGS['DESCRIPTION'],
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="example@gmail.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/users/', include('users.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/tattoos/', include('tattoos.urls')),
]

# Optional debug toolbar for development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
