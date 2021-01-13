import logging

from django.shortcuts import render
from django.views import View
from django.http import FileResponse, Http404

from TZ_Django_test.settings.dev import DOC_FILE_URL
from docs import models
import requests
from django.utils.encoding import escape_uri_path

logger = logging.getLogger()


def doc(request):
    docs = models.Docs.objects.only('image_url', 'desc', 'title').filter(is_delete=False)
    return render(request, 'doc/docDownload.html', locals())


class DocDownload(View):

    def get(self, request, doc_id):
        doc_file = models.Docs.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
        if doc_file:
            # /media/流畅的Python.pdf
            doc_url = doc_file.file_url

            doc_url = DOC_FILE_URL + doc_url
            # a = requests.get(doc_url)
            # res = HttpResponse(a)
            try:
                res = FileResponse(requests.get(doc_url))
            except Exception as e:
                logger.info("获取文档内容出现异常：\n{}".format(e))
                raise Http404("文档下载异常！")
            ex_name = doc_url.split('.')[-1]  # pdf

            if not ex_name:
                raise Http404('文件名异常')
            else:
                ex_name = ex_name.lower()

            if ex_name == "pdf":
                res["Content-type"] = "application/pdf"

            elif ex_name == "zip":
                res["Content-type"] = "application/zip"

            elif ex_name == "doc":
                res["Content-type"] = "application/msword"

            elif ex_name == "xls":
                res["Content-type"] = "application/vnd.ms-excel"

            elif ex_name == "docx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            elif ex_name == "ppt":
                res["Content-type"] = "application/vnd.ms-powerpoint"

            elif ex_name == "pptx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

            else:
                raise Http404('文件格式不正确')

            doc_filename = escape_uri_path(doc_url.split('/')[-1])

            # attachment  保存  inline 显示
            res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
            return res

        else:
            raise Http404('文档不存在')




