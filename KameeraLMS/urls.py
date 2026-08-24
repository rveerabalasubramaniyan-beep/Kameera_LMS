from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # ============================================================
    # LMS APPLICATION
    #
    # IMPORTANT:
    # This must come BEFORE Django's built-in admin URL.
    # Your custom routes such as:
    #
    # /admin/dashboard/
    # /admin/dashboard/courses/
    #
    # are inside lms/urls.py
    # ============================================================

    path(
        "",
        include("lms.urls")
    ),


    # ============================================================
    # DJANGO BUILT-IN ADMIN
    #
    # /admin/
    # ============================================================

    path(
        "admin/",
        admin.site.urls
    ),

]


# ================================================================
# MEDIA FILES
# ================================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )