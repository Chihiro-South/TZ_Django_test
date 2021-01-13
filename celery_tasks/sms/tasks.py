import logging

from TZ_Django_test.utils.yuntongxun.sms import CCP
from celery_tasks.main import celery_app
from celery_tasks.sms import constants

logger = logging.getLogger("django")

# retry_backoff  异步自动重试时间

@celery_app.task(bind=True,name='send_sms_code', retry_backoff=3)
def send_sms_code(self,mobile, sms_code):
    """
    发送短信验证码
    :param mobile: 手机号
    :param sms_code: 验证码时效
    :return: None
    """

    time = constants.SMS_CODE_EXPIRES
    try:
        ccp = CCP()
        send_res = ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_CODE_TEMP_ID)
        print(send_res)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
        raise self.retry(exc=e,max_retries=3)
    if send_res != 0:
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)
    return send_res
