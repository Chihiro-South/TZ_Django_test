from django.urls import path

from qauth import views

app_name = 'qauth'

urlpatterns = [
    path('qq/',views.QQAuthView.as_view(),name='qq_login'),
    path('auth_callback/', views.QQUserView.as_view(), name='auth_callback'),
]