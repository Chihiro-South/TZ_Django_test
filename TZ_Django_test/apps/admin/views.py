from datetime import datetime
import json
import logging
from collections import OrderedDict
from urllib.parse import urlencode

import qiniu
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views import View

from TZ_Django_test.settings.dev import FDFS_URL
from TZ_Django_test.utils.fastdfs.fdfs import FDFS_Client
from TZ_Django_test.utils.res_code import Code, error_map, res_json
from TZ_Django_test.utils.secrets import qiniu_secret_info
from admin import forms
from admin.scripts import get_page_data
from courses.models import Course, Teacher, CourseCategory
from docs.models import Docs
from news import models
from users.models import Users

params_status = res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
logger = logging.getLogger()


class IndexView(View):
    """
    """

    def get(self, request):
        return render(request, 'admin/index/index.html')


class TagsManageView(View):

    def get(self, request):
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')).filter(
            is_delete=False).order_by('num_news')
        return render(request, 'admin/news/tags_manage.html', locals())

    def post(self, request):
        js_str = request.body
        if not js_str:
            return params_status
        tag_name = json.loads(js_str)
        name = tag_name.get('name')
        if name:
            name = name.strip()
            # 深度学习   深度学习    元组 旧 obj False
            tag = models.Tag.objects.get_or_create(name=name)
            if tag[-1]:
                return res_json(errno=Code.OK)
            else:
                return res_json(errno=Code.DATAEXIST, errmsg='名字重复')
            # return (res_json(errno=Code.OK) if tag[-1] else res_json(errno=Code.DATAEXIST, errmsg='名字重复'))

        else:
            return res_json(errno=Code.NODATA, errmsg=error_map[Code.NODATA])

    def put(self, request, tag_id):
        json_data = request.body
        if not json_data:
            return params_status
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        tag_name = dict_data.get('name')
        tag = models.Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            if tag_name and tag_name.strip():
                # 有查询集有数据就返回True ,否则返回False
                if not models.Tag.objects.only('id').filter(name=tag_name).exists():
                    tag.name = tag_name
                    tag.save(update_fields=['name'])
                    return res_json(errmsg="标签更新成功")
                else:
                    return res_json(errno=Code.DATAEXIST, errmsg="标签名已存在")
            else:
                return res_json(errno=Code.PARAMERR, errmsg="标签名为空")

        else:
            return res_json(errno=Code.PARAMERR, errmsg="需要更新的标签不存在")

    def delete(self, request, tag_id):
        tag = models.Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            tag.delete()
            return res_json(errmsg="标签更新成功")
        else:
            return res_json(errno=Code.PARAMERR, errmsg="需要删除的标签不存在")


class HotNewsManageView(View):
    """
    """
    def get(self, request):
        hot_news = models.HotNews.objects.select_related('news__tag'). \
                       only('news_id', 'news__title', 'news__tag__name', 'priority'). \
                       filter(is_delete=False).order_by('priority', '-news__clicks')

        return render(request, 'admin/news/news_hot.html', locals())


class HotNewsDeleteView(View):

    def delete(self, request, hotnews_id):
        hotnews = models.HotNews.objects.only('id').filter(id=hotnews_id).first()
        if hotnews:
            hotnews.is_delete = True
            hotnews.save(update_fields=['is_delete'])
            return res_json(errmsg="热门文章删除成功")
        else:
            return res_json(errno=Code.PARAMERR, errmsg="需要删除的热门文章不存在")

    def put(self, request, hotnews_id):
        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.HotNews.PRI_CHOICES]
            if priority not in priority_list:
                return res_json(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')
        except Exception as e:
            logger.info('热门文章优先级异常：\n{}'.format(e))
            return res_json(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')

        hotnews = models.HotNews.objects.only('id').filter(id=hotnews_id).first()
        if not hotnews:
            return res_json(errno=Code.PARAMERR, errmsg="需要更新的热门文章不存在")

        if hotnews.priority == priority:
            return res_json(errno=Code.PARAMERR, errmsg="热门文章的优先级未改变")

        hotnews.priority = priority
        hotnews.save(update_fields=['priority'])
        return res_json(errmsg="热门文章更新成功")


class HotNewsAddView(View):
    """
    route: /admin/hotnews/add/
    """

    def get(self, request):
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')). \
            filter(is_delete=False).order_by('-num_news', 'update_time')
        priority_dict = OrderedDict(models.HotNews.PRI_CHOICES)

        return render(request, 'admin/news/news_hot_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            news_id = int(dict_data.get('news_id'))
        except Exception as e:
            logger.info('前端传过来的文章id参数异常：\n{}'.format(e))
            return res_json(errno=Code.PARAMERR, errmsg='参数错误')

        if not models.News.objects.filter(id=news_id).exists():
            return res_json(errno=Code.PARAMERR, errmsg='文章不存在')

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.HotNews.PRI_CHOICES]
            if priority not in priority_list:
                return res_json(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')
        except Exception as e:
            logger.info('热门文章优先级异常：\n{}'.format(e))
            return res_json(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')

        # 创建热门新闻
        hotnews_tuple = models.HotNews.objects.get_or_create(news_id=news_id)
        hotnews, is_created = hotnews_tuple
        hotnews.priority = priority  # 修改优先级
        hotnews.save(update_fields=['priority'])
        return res_json(errmsg="热门文章创建成功")


class NewsByTagIdView(View):
    """
    route: /admin/tags/<int:tag_id>/news/
    """
    def get(self, request, tag_id):
        newses = models.News.objects.values('id', 'title').filter(is_delete=False, tag_id=tag_id)
        news_list = [i for i in newses]

        return res_json(data={
            'news': news_list
        })


class NewsManage(View):
    def get(self,request):
        start_time = request.GET.get('start_time','')
        # 2019/12/12  把字符串格式转乘 日期格式
        start_time = datetime.strptime(start_time,'%Y/%m/%d')  if start_time else ''
        end_time = request.GET.get('end_time','')
        end_time = datetime.strptime(end_time, '%Y/%m/%d') if end_time else ''

        newses = models.News.objects.only('title','author__username','tag__name','update_time').filter(is_delete=False)
        # 单选开始 没选结束    返回比开始时间大的数据
        if start_time and not end_time:
            newses = newses.filter(update_time__gte=start_time)
            # 单选结束 没选开始    返回比结束时间小的数据
        if end_time and not start_time:
            newses = newses.filter(update_time__lte=end_time)
            # 结束 开始都有    返回开始和结束实时间之间的数据
        if start_time and end_time:
            newses = newses.filter(update_time__range=(start_time,end_time))

        # 处理标题   模糊查询
        title = request.GET.get('title','')
        if title:
            newses = newses.filter(title__icontains=title)
        # 模糊查询
        author_name = request.GET.get('author_name','')
        if author_name:
            newses = newses.filter(author__username__icontains=author_name)
        # 处理分类
        tags = models.Tag.objects.only('name').filter(is_delete=False)
        tag_id = int(request.GET.get('tag_id',0))
        newses = newses.filter(is_delete=False,tag_id=tag_id) or newses.filter(is_delete=False)
        # 处理分页
        try:
            page = int(request.GET.get('page',1))
        except Exception as e:
            logger.info('页面错误')
            page = 1

        pt = Paginator(newses,6)
        try:
            news_info = pt.page(page)
        except EmptyPage:
            logger.info('页码错误')
            news_info = pt.page(pt.num_pages)
        # 自定义分页器
        pages_data = get_page_data(pt,news_info)
        # 把日期格式转 字符串格式
        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if end_time else ''

        data = {
            'news_info':news_info,
            'tags':tags,
            'paginator':pt,
            'start_time':start_time,
            'end_time':end_time,
            'title':title,
            'author_name':author_name,
            'tag_id':tag_id,
            'other_param':urlencode({
                'start_time':start_time,
                'end_time':end_time,
                'title':title,
                'author_name':author_name,
                'tag_id':tag_id,

            })
        }
        data.update(pages_data)

        return render(request,'admin/news/news_manage.html',context=data)


class NewsEditView(View):

    def get(self, request, news_id):

        news = models.News.objects.filter(is_delete=False,id=news_id).first()
        if news:
            tags = models.Tag.objects.only('id','name').filter(is_delete=False)
            context = {
                'tags': tags,
                'news': news,
            }
            return render(request, 'admin/news/news_pub.html',locals())

        else:
            raise Http404('需要更新的文章不存在')

    def delete(self,request, news_id):
        """
        1.校验文章是否存在
        2.删除数据
        3.返回前端 True/False
        :param request:
        :param news_id:
        :return:
        """
        news = models.News.objects.only('id').filter(id=news_id).first()
        if news:
            news.is_delete = True
            news.save(update_fields = ['is_delete'])
            return res_json(errmsg="文章删除成功")
        else:
            return res_json(errno=Code.PARAMERR, errmsg="需要删除的文章不存在")

    def put(self, request, news_id):
        """
        更新文章
        :param request:
        :param news_id:
        :return:
        """
        news = models.News.objects.filter(is_delete=False, id=news_id).first()
        if not news:
            return res_json(errno=Code.NODATA, errmsg='需要更新的文章不存在')

        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.NewsPubForm(data=dict_data)
        if form.is_valid():
            news.title = form.cleaned_data.get('title')
            news.digest = form.cleaned_data.get('digest')
            news.content = form.cleaned_data.get('content')
            news.image_url = form.cleaned_data.get('image_url')
            news.tag = form.cleaned_data.get('tag')
            news.save()
            return res_json(errmsg='文章更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return res_json(errno=Code.PARAMERR, errmsg=err_msg_str)


class NewsPubView(View):

    def get(self,request):
        """
        1.获取文章标签
        2.渲染文章发布页
        :param request:
        :return:
        """
        tags = models.Tag.objects.only('id','name').filter(is_delete=False)
        # 后台登录成功后，删除user，包括news_pub.js,news_pub.html
        user = Users.objects.only('id', 'username')

        return render(request, 'admin/news/news_pub.html', locals())

    def post(self,request):

        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        print(dict_data)
        form = forms.NewsPubForm(data=dict_data)
        if form.is_valid():
            news_instance = form.save(commit=False)
            news_instance.author_id = request.user.id
            news_instance.save()

            return res_json(errmsg='文章创建成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return res_json(errno=Code.PARAMERR, errmsg=err_msg_str)


class NewsUploadImage(View):

    def post(self, request):
        # request.FILES.get('image_file') 获取图片对象
        image_file = request.FILES.get('image_file')
        if not image_file:
            logger.info('从前端获取图片失败')
            return res_json(errno=Code.NODATA, errmsg='从前端获取图片失败')
        # 文件类型有content_type这个属性
        if image_file.content_type not in ('image/jpeg', 'image/png', 'image/gif'):
            return res_json(errno=Code.DATAERR, errmsg='不能上传非图片文件')

        # image_file.name 文件名
        try:
            image_ext_name = image_file.name.split('.')[-1]
        except Exception as e:
            logger.info('图片拓展名异常：{}'.format(e))
            image_ext_name = 'jpg'

        try:
            # 前端传的是文件 需要通过upload_by_buffer() 方法，
            upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.error('图片上传出现异常：{}'.format(e))
            return res_json(errno=Code.UNKOWNERR, errmsg='图片上传异常')
        else:
            # 此处有个点Upload successed.
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('图片上传到FastDFS服务器失败')
                return res_json(Code.UNKOWNERR, errmsg='图片上传到服务器失败')
            else:
                image_name = upload_res.get('Remote file_id')
                image_url = FDFS_URL + image_name
                return res_json(data={'image_url': image_url}, errmsg='图片上传成功')


class UploadToken(View):

    def get(self, request):
        access_key = qiniu_secret_info.QI_NIU_ACCESS_KEY
        secret_key = qiniu_secret_info.QI_NIU_SECRET_KEY
        bucket_name = qiniu_secret_info.QI_NIU_BUCKET_NAME
        # 构建鉴权对象
        q = qiniu.Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        # 最好直接返回原生js
        return JsonResponse({"uptoken": token})


class BannerManageView(View):

    def get(self, request):
        priority_dict = OrderedDict(models.Banner.PRI_CHOICES)
        banners = models.Banner.objects.only('image_url', 'priority').filter(is_delete=False)
        return render(request, 'admin/news/news_banner.html', locals())


class BannerEditView(View):

    def delete(self, request, banner_id):
        banner = models.Banner.objects.only('id').filter(id=banner_id).first()
        if banner:
            banner.is_delete = True
            banner.save(update_fields=['is_delete'])
            return res_json(errmsg="轮播图删除成功")
        else:
            return res_json(errno=Code.PARAMERR, errmsg="需要删除的轮播图不存在")

    def put(self, request, banner_id):
        banner = models.Banner.objects.only('id').filter(id=banner_id).first()
        if not banner:
            return res_json(errno=Code.PARAMERR, errmsg="需要更新的轮播图不存在")

        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.Banner.PRI_CHOICES]
            if priority not in priority_list:
                return res_json(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')
        except Exception as e:
            logger.info('轮播图优先级异常：\n{}'.format(e))
            return res_json(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')

        image_url = dict_data.get('image_url')
        if not image_url:
            return res_json(errno=Code.PARAMERR, errmsg='轮播图url为空')

        if banner.priority == priority and banner.image_url == image_url:
            return res_json(errno=Code.PARAMERR, errmsg="轮播图的参数未改变")

        banner.priority = priority
        banner.image_url = image_url
        banner.save(update_fields=['priority', 'image_url'])
        return res_json(errmsg="轮播图更新成功")


class BannerAddView(View):

    def get(self, request):
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')). \
            filter(is_delete=False).order_by('-num_news', 'update_time')
        # 优先级列表
        # priority_list = {K: v for k, v in models.Banner.PRI_CHOICES}
        priority_dict = OrderedDict(models.Banner.PRI_CHOICES)

        return render(request, 'admin/news/news_banner_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            news_id = int(dict_data.get('news_id'))
        except Exception as e:
            logger.info('前端传过来的文章id参数异常：\n{}'.format(e))
            return res_json(errno=Code.PARAMERR, errmsg='参数错误')

        if not models.News.objects.filter(id=news_id).exists():
            return res_json(errno=Code.PARAMERR, errmsg='文章不存在')

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.Banner.PRI_CHOICES]
            if priority not in priority_list:
                return res_json(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')
        except Exception as e:
            logger.info('轮播图优先级异常：\n{}'.format(e))
            return res_json(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')

        # 获取轮播图url
        image_url = dict_data.get('image_url')
        if not image_url:
            return res_json(errno=Code.PARAMERR, errmsg='轮播图url为空')

        # 创建轮播图
        banners_tuple = models.Banner.objects.get_or_create(news_id=news_id)
        banner, is_created = banners_tuple

        banner.priority = priority
        banner.image_url = image_url
        banner.save(update_fields=['priority', 'image_url'])
        return res_json(errmsg="轮播图创建成功")


class DocsManageView(View):

    def get(self, request):
        docs = Docs.objects.only('title', 'create_time').filter(is_delete=False)
        return render(request, 'admin/docs/docs_manage.html', locals())


class DocsEditView(View):

    def get(self, request, doc_id):
        """
        """
        doc = Docs.objects.filter(is_delete=False, id=doc_id).first()
        if doc:
            tags = Docs.objects.only('id', 'name').filter(is_delete=False)
            context = {
                'doc': doc
            }
            return render(request, 'admin/docs/docs_pub.html', context=context)
        else:
            raise Http404('需要更新的文章不存在！')

    def delete(self, request, doc_id):
        doc = Docs.objects.filter(is_delete=False, id=doc_id).first()
        if doc:
            doc.is_delete = True
            doc.save(update_fields=['is_delete'])
            return res_json(errmsg="文档删除成功")
        else:
            return res_json(errno=Code.PARAMERR, errmsg="需要删除的文档不存在")

    def put(self, request, doc_id):
        doc = Docs.objects.filter(is_delete=False, id=doc_id).first()
        if not doc:
            return res_json(errno=Code.NODATA, errmsg='需要更新的文档不存在')

        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.DocsPubForm(data=dict_data)
        if form.is_valid():
            doc.title = form.cleaned_data.get('title')
            doc.desc = form.cleaned_data.get('desc')
            doc.file_url = form.cleaned_data.get('file_url')
            doc.image_url = form.cleaned_data.get('image_url')
            doc.save()
            return res_json(errmsg='文档更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return res_json(errno=Code.PARAMERR, errmsg=err_msg_str)


class DocsPubView(View):

    def get(self, request):

        return render(request, 'admin/docs/docs_pub.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.DocsPubForm(data=dict_data)
        if form.is_valid():
            docs_instance = form.save(commit=False)
            docs_instance.author_id = request.user.id
            docs_instance.save()
            return res_json(errmsg='文档创建成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return res_json(errno=Code.PARAMERR, errmsg=err_msg_str)


class DocsUploadFile(View):

    def post(self, request):
        text_file = request.FILES.get('text_file')
        if not text_file:
            logger.info('从前端获取文件失败')
            return res_json(errno=Code.NODATA, errmsg='从前端获取文件失败')

        if text_file.content_type not in ('application/octet-stream', 'application/pdf',
                                          'application/zip', 'text/plain', 'application/x-rar'):
            return res_json(errno=Code.DATAERR, errmsg='不能上传非文本文件')

        try:
            text_ext_name = text_file.name.split('.')[-1]
        except Exception as e:
            logger.info('文件拓展名异常：{}'.format(e))
            text_ext_name = 'pdf'

        try:
            upload_res = FDFS_Client.upload_by_buffer(text_file.read(), file_ext_name=text_ext_name)
        except Exception as e:
            logger.error('文件上传出现异常：{}'.format(e))
            return res_json(errno=Code.UNKOWNERR, errmsg='文件上传异常')
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('文件上传到FastDFS服务器失败')
                return res_json(Code.UNKOWNERR, errmsg='文件上传到服务器失败')
            else:
                text_name = upload_res.get('Remote file_id')
                text_url = FDFS_URL + text_name
                return res_json(data={'text_file': text_url}, errmsg='文件上传成功')


class CoursesManageView(View):

    def get(self, request):
        courses = Course.objects.select_related('category', 'teacher').\
            only('title', 'category__name', 'teacher__name').filter(is_delete=False)
        return render(request, 'admin/course/courses_manage.html', locals())


class CoursesEditView(View):

    def get(self, request, course_id):
        """
        """
        course = Course.objects.filter(is_delete=False, id=course_id).first()
        if course:
            teachers = Teacher.objects.only('name').filter(is_delete=False)
            categories = CourseCategory.objects.only('name').filter(is_delete=False)
            return render(request, 'admin/course/courses_pub.html', locals())
        else:
            raise Http404('需要更新的课程不存在！')

    def delete(self, request, course_id):
        course = Course.objects.filter(is_delete=False, id=course_id).first()
        if course:
            course.is_delete = True
            course.save(update_fields=['is_delete'])
            return res_json(errmsg="课程删除成功")
        else:
            return res_json(errno=Code.PARAMERR, errmsg="需要删除的课程不存在")

    def put(self, request, course_id):
        course = Course.objects.filter(is_delete=False, id=course_id).first()
        if not course:
            return res_json(errno=Code.NODATA, errmsg='需要更新的课程不存在')

        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.CoursesPubForm(data=dict_data)
        if form.is_valid():
            for attr, value in form.cleaned_data.items():
                setattr(course, attr, value)

            course.save()
            return res_json(errmsg='课程更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return res_json(errno=Code.PARAMERR, errmsg=err_msg_str)


class CoursesPubView(View):

    def get(self, request):
        teachers = Teacher.objects.only('name').filter(is_delete=False)
        categories = CourseCategory.objects.only('name').filter(is_delete=False)
        return render(request, 'admin/course/courses_pub.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.CoursesPubForm(data=dict_data)
        if form.is_valid():
            courses_instance = form.save()
            return res_json(errmsg='课程发布成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return res_json(errno=Code.PARAMERR, errmsg=err_msg_str)
