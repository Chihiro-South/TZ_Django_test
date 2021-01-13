from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager

# Create your models here.
class UserManager(_UserManager):

    def create_superuser(self, username, password, email=None, **extra_fields):
        return super(UserManager, self).create_superuser(username=username,password=password, email=email, **extra_fields)


class Users(AbstractUser):

    objects = UserManager()
    REQUIRED_FIELDS = ['mobile']
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号", help_text='手机号',error_messages={'unique': "此手机号已注册"})   # 指定报错的中文信息
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = "tb_users"   # 指明数据库表名
        verbose_name = "用户"    # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):  # 打印对象时调用
        return self.username
