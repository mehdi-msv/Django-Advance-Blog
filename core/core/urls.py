"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.documentation import include_docs_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import cache_page

from blog.sitemaps import PostSitemap


schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version="v1",
        description="This is the API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mehdi.mousavi.rad1@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

sitemaps = {
    "posts": PostSitemap(),
}

# Default URL configuration for the core project.
urlpatterns = [
    path("", RedirectView.as_view(url="/blog/")),
    path("admin/", admin.site.urls),
    path("blog/", include("blog.urls")),
    path("accounts/", include("accounts.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "api-docs/", include_docs_urls(title="Blog API")
    ),  # API documentation
    path(
        "swagger.<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path(
        "sitemap.xml",
        cache_page(86400)(sitemap),
        {"sitemaps": sitemaps},
        name="cached-sitemap",
    ),
    path("robots.txt", include("robots.urls")),
]

handler400 = "core.views.errors.error_400"  # bad request
handler403 = "core.views.errors.error_403"  # permission denied
handler404 = "core.views.errors.error_404"  # page not found
handler500 = "core.views.errors.error_500"  # server error

# Serving static and media for development
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
