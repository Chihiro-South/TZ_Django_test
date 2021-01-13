import random
import json
import logging
from django.views import View
from django_redis import get_redis_connection
from django.http import HttpResponse
from TZ_Django_test.utils.captcha.captcha import captcha
from TZ_Django_test.utils.res_code import res_json, Code
from TZ_Django_test.utils.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_code
from users.models import Users

# 导入日志器
logger = logging.getLogger('django')


class ImageCode(View):
    """
    define image verification view
    # /image_codes/<uuid:image_code_id>/
    """
    def get(self, request, image_code_id):
        name, text, image = captcha.generate_captcha()
        con_redis = get_redis_connection(alias='verify_codes')
        img_key = "img_{}".format(image_code_id).encode('utf-8')
        # 将图片验证码的key和验证码文本保存到redis中，并设置过期时间
        con_redis.setex(img_key,300, text)
        logger.info("Image code: {}".format(text))
        # HttpResponse(content=响应体, content_type=响应体数据类型, status=状态码)
        return HttpResponse(content=image, content_type="image/jpg")


class CheckUsernameView(View):

    def get(self, request, username):
        data = {
            'username': username,
            'count': Users.objects.filter(username=username).count()
        }
        return res_json(data=data)


class CheckMoblieView(View):

    def get(self, request, mobile):
        data = {
            'mobile': mobile,
            'count': Users.objects.filter(mobile=mobile).count()
        }
        return res_json(data=data,)


class SMSCodeView(View):
    def post(self, request):
        json_str = request.body
        if not json_str:
            return res_json(errno=Code.PARAMERR, errmsg='参数错误')
        dict_data = json.loads(json_str)

        image_code_client = dict_data.get('text')
        uuid = dict_data.get('image_code_id')
        mobile = dict_data.get('mobile')
        # 校验参数
        if not all([image_code_client, uuid, mobile]):
            return res_json(errno=Code.PARAMERR, errmsg='参数错误')
        # 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_codes')
        # 提取数据库的图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            # 图形验证码过期或者不存在
            return res_json(errno=Code.PARAMERR, errmsg='参数错误')
        # 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        # 对比图形验证码
        image_code_server = image_code_server.decode()  # bytes转字符串
        if image_code_client.lower() != image_code_server.lower():  # 转小写后比较
            return res_json(errno=Code.PARAMERR, errmsg='输入图形验证码有误')

        # 生成短信验证码：生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 限定频繁发送验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return res_json(errno=Code.DATAEXIST, errmsg='发送短信过于频繁')

        redis_conn.setex('sms_%s' % mobile, 60, sms_code)
        # 重新写入send_flag
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        # 执行请求
        # 发送短信
        logger.info('短信验证码: {}'.format(sms_code))
        logging.info('发送短信正常[mobile:%s sms_num:%s]' % (mobile, sms_code))

        # 发送短信验证码
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, 5], 1)
        send_sms_code.delay(mobile, sms_code)
        # 响应结果
        return res_json(errmsg='短信验证码发送成功')
#
# class SMSCodeView(GenericAPIView):
#     """
#     短信验证码
#     """
#     serializer_class = serializers.CheckImageCodeSerialzier
#
#     def get(self, request, mobile):
#         """
#         创建短信验证码
#         """
#         # 判断图片验证码, 判断是否在60s内
#         serializer = self.get_serializer(data=request.query_params)
#         # 校验
#         serializer.is_valid(raise_exception=True)
#
#         # 生成短信验证码
#         sms_code = "%06d" % random.randint(0, 999999)
#         print("短信验证码内容是：%s" % sms_code)
#
#         # 保存短信验证码与发送记录
#         redis_conn = get_redis_connection('verify_codes')
#         pl = redis_conn.pipeline()
#         # 短讯验证码有效期
#         pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
#         # 短讯验证码发送间隔
#         pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
#         pl.execute()
#
#         # 发送短信验证码
#         send_sms_code(mobile, sms_code)
#
#         return Response({"message": "OK"}, status.HTTP_200_OK)
#
#
# class SMSCodeByTokenView(APIView):
#     """根据access_token发送短信"""
#
#     def get(self, request):
#         # 获取并校验 access_token
#         access_token = request.query_params.get('access_token')
#         if not access_token:
#             return Response({"message": "缺少access token"}, status=status.HTTP_400_BAD_REQUEST)
#
#         # 从access_token中取出手机号
#         mobile = Users.check_send_sms_code_token(access_token)
#         if mobile is None:
#             return Response({"message": "无效的access token"}, status=status.HTTP_400_BAD_REQUEST)
#
#         # 判断手机号发送的次数
#         redis_conn = get_redis_connection('verify_codes')
#         send_flag = redis_conn.get('send_flag_%s' % mobile)
#         if send_flag:
#             return Response({"message": "发送短信次数过于频"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
#
#         # 生成短信验证码
#         sms_code = '%06d' % random.randint(0, 999999)
#         print('短信验证码{}'.format(sms_code))
#
#         # 使用redis的pipeline管道一次执行多个命令
#         pl = redis_conn.pipeline()
#         pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
#         pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
#         # 让管道执行命令
#         pl.execute()
#
#         # 发送短信
#         # ccp = CCP()
#         # time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
#         # ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_CODE_TEMP_ID)
#         # 使用celery发布异步任务
#         send_sms_code(mobile, sms_code)
#
#         # 返回
#         return Response({'message': 'OK'})