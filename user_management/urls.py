from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from user_management.views import CheckUserStateView, UserLoginView, VerifyOtpView, CompleteProfileView

urlpatterns = [
    path("auth/check-mobile", CheckUserStateView.as_view(), name='check-mobile'),
    path("auth/login", UserLoginView.as_view(), name='login'),
    path("auth/verify-otp", VerifyOtpView.as_view(), name='verify-otp'),
    path("auth/complete-profile", CompleteProfileView.as_view(), name='complete-profile'),
]