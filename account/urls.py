from django.urls import path

from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name="register" ),
    path('login/',views.LoginView.as_view(), name="login" ),
    path('activate/<uidb64>/<token>/',views.ActivateView.as_view(), name='activate'),
    path('logout/',views.LogoutView.as_view(), name="logout" ),
]
