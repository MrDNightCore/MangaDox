# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_page, name="login_page"),
    path("registers/", views.register_page, name="register_page"),
    path("logout/", views.logout_page, name="logout_page"),
]

# Custom CSRF failure handler
handler403 = 'users.views.csrf_failure'
