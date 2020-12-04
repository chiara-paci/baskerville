from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.urls import path

#from django_registration.backends.activation.views import RegistrationView,ActivationView

app_name="baskervilleauth"

# django auth
urlpatterns=[
    path('login/', 
         auth_views.LoginView.as_view(), 
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), 
         name='logout'),
    path('password_change/', 
         login_required(auth_views.PasswordChangeView.as_view(success_url=reverse_lazy("baskervilleauth:password_change_done"))), 
         name="password_change"),
    path('password_change/done/', 
         login_required(auth_views.PasswordChangeDoneView.as_view()), 
         name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(success_url=reverse_lazy("baskervilleauth:password_reset_done")), 
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy("baskervilleauth:password_reset_complete")), 
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
]
