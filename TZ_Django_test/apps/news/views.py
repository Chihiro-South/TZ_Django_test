import logging
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from haystack.views import SearchView

from TZ_Django_test.utils.res_code import res_json, Code, error_map
from .models import News, Tag, Banner, HotNews, Comments
from django.views import View
from django.contrib.auth.decorators import login_required

logger = logging.getLogger()


# 自定义装饰器，验证用户是否登录
def login_req(f):
    def func(request):
        if request.user.is_authenticated:
            return f(request)
        else:
            return redirect('/user/login')

    return func


# 测试视频
# def index(request):
#     return render(request, 'course/videos.html')


# 首页
# @login_required(login_url='/user/login/')   # 必须登录后才可进入首页面
# @login_req
def index(request):
    """
    """
    tags = Tag.objects.filter(is_delete=False).only('name')
    click_hot = News.objects.only('title', 'image_url', 'update_time', 'author__username', 'tag__name').select_related(
        'tag', 'author').order_by('-clicks')[0:2]
    hot = HotNews.objects.select_related('news').only('news__title', 'news__image_url').order_by('priority')

    return render(request, 'news/index.html', locals())


# 新闻列表
class NewsListView(View):
    def get(self, request):
        try:
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.error('页面或标签定义错误\n{}'.format(e))
            tag_id = 0
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.error('页面或标签定义错误\n{}'.format(e))
            page = 1
        news_list = News.objects.values('title', 'digest', 'image_url', 'update_time', 'id').annotate(
            tag_name=F('tag__name'), author=F('author__username'))
        news = news_list.filter(tag_id=tag_id, is_delete=False) or news_list.filter(is_delete=False)

        pager = Paginator(news, 5)
        try:
            news_info = pager.page(page)  # 拿到当前页返回
        except Exception as e:
            logger.error(e)
            news_info = pager.page(pager.num_pages)
        data = {
            'news': list(news_info),
            'total_pages': pager.num_pages
        }
        return res_json(data=data)


# 新闻详情
class NewsDetailView(View):
    def get(self, request, news_id):

        news = News.objects.select_related('tag', 'author').only('title', 'content', 'update_time', 'tag__name',
                                                                 'author__username').filter(is_delete=False,
                                                                                            id=news_id).first()
        News.increase_clicks(news)
        comments = Comments.objects.select_related('author', 'parent').only('author__username', 'update_time',
                                                                            'parent__update_time').filter(
            is_delete=False, news_id=news_id)
        comments_list = []
        for comm in comments:
            comments_list.append(comm.to_dict_data())
        #     if not comm.parent:
        #         data = {
        #             'news_id': comm.news_id,
        #             'content_id': comm.id,
        #             'content': comm.content,
        #             'author': comm.author.username,
        #             'update_time': comm.update_time,
        #             'child_list': []
        #         }
        #         comments_list.append(data)
        #
        # for comm in comments:
        #     if comm in comments:
        #         for parent_comment in comments_list:
        #             if comm.parent_id == parent_comment['content_id']:
        #                 parent_comment['child_list'].append(comm)

        if news:
            return render(request, 'news/news_detail.html', locals())
        else:
            return HttpResponseNotFound('PAGE NOT FOUND')


# 轮播图
class BannerView(View):
    def get(self, request):
        banner = Banner.objects.only('image_url', 'news__title').select_related('news').filter(
            is_delete=False).order_by('priority')  # 从1到6
        banner_info = []
        for i in banner:
            banner_info.append({
                'image_url': i.image_url,
                'news_title': i.news.title,
                'news_id': i.news.id
            })
        data = {
            'banners': banner_info
        }
        return res_json(data=data)


# 追加评论数据
class CommentsView(View):

    def post(self, request, news_id):

        if not request.user.is_authenticated:
            return res_json(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])

        if not News.objects.only('id').filter(is_delete=False, id=news_id).exists():
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 获取参数
        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        dita_data = json.loads(json_data)

        # 一级评论
        content = dita_data['content']
        if not dita_data.get('content'):
            return res_json(errno=Code.PARAMERR, errmsg='评论内容不能为空')

        # 回复评论
        parent_id = dita_data.get('parent_id')
        if parent_id:
            if not Comments.objects.only('id').filter(is_delete=False, id=parent_id, news_id=news_id).exists():
                return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 保存数据库
        news_content = Comments()
        news_content.content = content
        news_content.news_id = news_id
        news_content.author = request.user
        news_content.parent_id = parent_id if parent_id else None
        news_content.save()
        return res_json(data=news_content.to_dict_data())


class Search(SearchView):
    template = 'news/search.html'

    def create_response(self):
        # 接收前台用户输入的查询值
        # kw='python'
        query = self.request.GET.get('q', '')
        if not query:
            show = True
            host_news = HotNews.objects.select_related('news').only(
                'news_id', 'news__title', 'news__image_url').filter(is_delete=False).order_by('priority')
            paginator = Paginator(host_news, 5)
            try:
                page = paginator.page(int(self.request.GET.get('page', 1)))
            # 假如传的不是整数
            except PageNotAnInteger:
                # 默认返回第一页
                page = paginator.page(int(1))

            except EmptyPage:
                page = paginator.page(paginator.num_pages)
            return render(self.request, self.template, locals())
        else:
            show = False
            return super().create_response()
