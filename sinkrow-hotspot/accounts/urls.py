from django.urls import path

from . import views
app_name='accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/<slug:username>', views.dashboard, name='dashboard'),
    path('logout/<slug:username>', views.logout_view, name='logout'),
    path('success/<slug:username>', views.success_view, name='success'),
    path('success/', views.success_view, name='success'),
    path('error/<slug:username>/<int:err>', views.error_view, name='err')
]
