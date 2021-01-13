from django.db import models

# Create your models here.


class QQUser(models.Model):
    create_tiem = models.DateTimeField(auto_now_add=True)
    update_tiem = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('users.Users',on_delete=models.CASCADE)
    openid = models.CharField(max_length=64, verbose_name='openid')
    class Meta:
        db_table = 'tb_qq'
        verbose_name = 'QQ绑定用户'
        verbose_name_plural = verbose_name
