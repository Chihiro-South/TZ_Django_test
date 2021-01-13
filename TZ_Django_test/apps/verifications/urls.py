from django.urls import re_path, path

from . import views

app_name = "verifications"

urlpatterns = [
    # image_code_id为uuid格式
    path('image_code/<uuid:image_code_id>/', views.ImageCode.as_view(), name='image_code'),
    re_path('username/(?P<username>\w{5,20})/', views.CheckUsernameView.as_view(), name='username'),
    re_path('mobiles/(?P<mobile>1[3-9]\d{9})/', views.CheckMoblieView.as_view(), name='mobile'),
    path('sms_code/', views.SMSCodeView.as_view(), name='sms_code'),
]
