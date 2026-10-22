from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/", include("library.urls")),
    # Login/logout da interface navegável do DRF (útil para testar pelo navegador)
    path("api-auth/", include("rest_framework.urls")),
]
