# tracker/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('report/', views.report_mobile, name='report_mobile'),
    path('success/', views.report_success, name='report_success'),
    path('search/', views.search_reports, name='search_reports'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='tracker/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
