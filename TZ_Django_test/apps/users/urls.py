from django.urls import path

from . import views

# urlpatterns是被django自动识别的路由列表变量

app_name = 'users'

urlpatterns = [
    # 每个路由信息都需要使用url函数来构造
    # url(路径, 视图)
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('changepwd/', views.ChangePasswd.as_view(), name='changepwd'),
    path('forgetpwd/',views.ForgetPwd.as_view(), name='forgetpwd')
]
