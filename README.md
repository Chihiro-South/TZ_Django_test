# TZ_Django_test

#### 介绍


#### 软件架构

软件架构说明

1. Python 第三方安装库

   ```shell
   
    pip install amqp==2.5.2
    pip install backcall==0.1.0
    pip install baidu-aip==2.2.18.0
    pip install bce-python-sdk==0.8.37
    pip install billiard==3.6.3.0
    pip install blessings==1.7
    pip install bpython==0.18
    pip install celery==4.4.2
    pip install certifi==2019.11.28
    pip install chardet==3.0.4
    pip install curtsies==0.3.1
    pip install decorator==4.4.2
    pip install Django==2.1.8
    pip install django-cors-headers==3.2.1   # 跨域
    pip install django-haystack==2.8.1
    pip install django-redis==4.11.0
    pip install django-stubs==1.5.0
    pip install djangorestframework==3.11.0
    pip install djangorestframework-stubs==1.1.0
    pip install elasticsearch==2.4.1
    pip install fdfs-client-py==1.2.6
    pip install future==0.18.2
    pip install greenlet==0.4.15
    pip install idna==2.9
    pip install ipython==6.2.0
    pip install ipython-genutils==0.2.0
    pip install itsdangerous==1.1.0
    pip install jedi==0.16.0
    pip install kombu==4.6.8
    pip install mutagen==1.44.0
    pip install mypy==0.770
    pip install mypy-extensions==0.4.3
    pip install nose==1.3.7
    pip install parso==0.6.2
    pip install pexpect==4.8.0
    pip install pickleshare==0.7.5
    pip install Pillow==7.0.0
    pip install pip==20.0.2
    pip install prompt-toolkit==1.0.18
    pip install ptyprocess==0.6.0
    pip install pycrypto==2.6.1
    pip install Pygments==2.6.1
    pip install PyMySQL==0.9.3
    pip install pytz==2019.3
    pip install qiniu==7.2.8
    pip install QQLoginTool==0.3.0
    pip install redis==3.4.1
    pip install requests==2.23.0
    pip install setuptools==46.0.0
    pip install simplegeneric==0.8.1
    pip install six==1.14.0
    pip install traitlets==4.3.3
    pip install typed-ast==1.4.1
    pip install typing-extensions==3.7.4.1
    pip install urllib3==1.25.8
    pip install vine==1.3.0
    pip install wcwidth==0.1.8
    pip install wheel==0.34.2
   
   ```

2. 启动服务

   ```shell
   
   cd /home/sed/Projects/TZ_Django_test
   # 异步服务:cd到celery_tasks同级目录中
   celery -A celery_tasks.main worker -l info
   # -A 选项指定 celery 实例 app 的位置
   # -l 选项指定日志级别， -l 是 --loglevel 的缩略形式
   
   # runserver:
   python manage.py runserver 0:8000
   
   ```  

3. 文件说明

   ```shell
   
   
   
   ```
