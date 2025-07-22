from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: render(request, 'home.html'), name='home'),
]
