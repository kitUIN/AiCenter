"""
URL configuration for AiCenter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include, re_path

from application import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="DRF TOOLS API",
        default_version="v1",
    ),
    public=True,
)

urlpatterns = [
                  re_path(
                      r"^swagger(?P<format>\.json|\.yaml)$",
                      schema_view.without_ui(cache_timeout=0),
                      name="schema-json",
                  ),
                  path(
                      "",
                      schema_view.with_ui("swagger", cache_timeout=0),
                      name="schema-swagger-ui",
                  ),
                  path(
                      r"redoc/",
                      schema_view.with_ui("redoc", cache_timeout=0),
                      name="schema-redoc",
                  ),
                  path('api-auth/', include('rest_framework.urls')),  # 添加这行
              ] + [re_path(ele.get('re_path'), include(ele.get('include'))) for ele in settings.PLUGINS_URL_PATTERNS]
