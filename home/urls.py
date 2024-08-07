# noinspection GrazieInspection
""" WAMFO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls.static import static
from django.conf import settings
from home.views import RecoverVitalityAPIList, RecoverVitalityAPI

urlpatterns = [
    # Admin

    # Student
    path('recover/vitality', RecoverVitalityAPI.as_view(), name='Recover Vitality'),
    path('recover/vitality/apply', RecoverVitalityAPIList.as_view(), name='Recover Vitality List'),

    # All
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
