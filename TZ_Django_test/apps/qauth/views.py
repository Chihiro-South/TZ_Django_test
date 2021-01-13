import json
from django.contrib.auth import login
from django.shortcuts import render, redirect, reverse
from QQLoginTool.QQtool import OAuthQQ
from django.views import View
from .models import QQUser
from TZ_Django_test.settings import dev
from django import http


class QQAuthView(View):

    def get(self, request):
        state = request.META['HTTP_REFERER']
        auth = OAuthQQ(
            client_id=dev.APP_ID,
            client_secret=dev.APP_KEY,
            redirect_uri=dev.RED_URL,
            state=state
        )
        login_url = auth.get_qq_url()
        # print(login_url)
        # return http.JsonResponse({'login_url': login_url})
        return redirect(login_url)


class QQUserView(View):
    def get(self,request):
        code = request.GET.get('code')
        auth = OAuthQQ(
            client_id=dev.APP_ID,
            client_secret=dev.APP_KEY,
            redirect_uri=dev.RED_URL,
        )
        # 根据code 获取 token
        token = auth.get_access_token(code)
        #2 根据toekn获取id
        openid = auth.get_open_id(token)
        try:
            qq = QQUser.objects.get(openid=openid)
        except:
            json_str = json.dumps({'openid' : openid})
            context = {
                'token' : json_str
            }

            return render(request,'users/qq_call_back.html',context)
        else:
            user = qq.user
            login(request,user)
            return redirect(reverse('news:index'))

    def post(self,request):
        """
        <QueryDict: {'access_token': ['{"openid": "0EAA9B257DA8C68AB03DFA35F3A0B566"}'], 'telephone': ['13535351112'], 'password': ['123456'], 'captcha_graph': ['XLZ7'], 'sms_captcha': ['360487']}>
        :param request:
        :return:
        """
        access_token = request.POST['access_token']
        mobile = request.POST['telephone']
        pad = request.POST['password']
        sms_code = request.POST['sms_captcha']
        if not all([access_token,mobile,pad,sms_code]):
            return http.HttpResponseForbidden('参数错误')
        import re
        if not re.match('^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden('参数错误')

        if not re.match('^[a-zA-Z0-9]{6,20}$',pad):
            return http.HttpResponseForbidden('参数错误')
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('verify_code')
        sms_num_s  = redis_conn.get('sms_'+ mobile).decode()
        if sms_num_s is None:
            return http.HttpResponseForbidden('参数错误')
        redis_conn.delete('sms_'+ mobile)
        redis_conn.delete('sms_flag_'+ mobile)
        if sms_code != sms_num_s:
            return http.HttpResponseForbidden('参数错误')
        openid_dict= json.loads(access_token)

        if openid_dict is None:
            return http.HttpResponseForbidden('授权信息无效')
        openid = openid_dict['openid']
        # 绑定用户
        from users.models import Users
        try:
            user = Users.objects.get(mobile=mobile)
        except:
            user = Users.objects.create_user(mobile,password=pad,mobile=mobile)
        else:
            if not user.check_password(pad):
                return http.HttpResponseForbidden('手机号已使用或者密码错误')
        #  注册用户
        QQUser.objects.create(user=user,openid=openid)
        login(request,user)
        import time
        time.sleep(2)
        return redirect('/')


"""

class QQAuthView(View):

    def get(self, request):
        state = request.META['HTTP_REFERER']
        auth = OAuthQQ(
            client_id=dev.APP_ID,
            client_secret=dev.APP_KEY,
            redirect_uri=dev.RED_URL,
            state=state
        )
        login_url = auth.get_qq_url()
        print(login_url)
        return redirect(login_url)

def demo(request):
    return HttpResponse(request ,"Hello World")

"""

