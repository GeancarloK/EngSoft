from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from login import views as li

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', li.first, name='first'),
    path('login/', li.login, name='login'),
    path('logout/', li.logoff, name='logout'),
    path('home/', li.home, name='home'),
    path('criar_predio/', li.criar_predio, name='criar_predio'),
]