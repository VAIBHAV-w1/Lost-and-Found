from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('report/', views.report_item, name='report_item'), 
    path('success/', views.report_success, name='report_success'),
    path('search/', views.search_reports, name='search_reports'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='tracker/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('message/<int:report_id>/', views.send_message, name='send_message'),
    path('resolve/<int:report_id>/', views.resolve_item, name='resolve_item'),
]
