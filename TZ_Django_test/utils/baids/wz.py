import re
from aip import AipOcr,AipBodyAnalysis,AipImageCensor
""" 你的 APPID AK SK """
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


# """ 读取图片 """
# with open(r'g.jpg', 'rb') as fp:
#     image = fp.read()
#
# # """ 调用通用文字识别, 图片参数为本地图片 """
# data = client.basicGeneralUrl(image)
# # data = str(data)
# # print(data)
# res = data['words_result'][0]['words']
# print(res)
# clients = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)
# """ 读取图片 """
# def get_file_content(filePath):
#     with open(filePath, 'rb') as fp:
#         return fp.read()
#
# image = get_file_content('./images/10.jpg')
#
# # """ 调用人体检测与属性识别 """
# clients.bodyAttr(image)
#
# # """ 如果有可选参数 """
# options = {}
# options["age"] = "gender,age,upper_color"
#
# # """ 带参数调用人体检测与属性识别 """
# res = clients.bodyAttr(image, options)
# # print(res)
# c = res['person_info'][0]['attributes']
# # print(c)
# for k,v in c.items():
#     print(k,v['name'])


# 图片鉴黄
s_client = AipImageCensor(APP_ID, API_KEY, SECRET_KEY)
""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

""" 调用色情识别接口 """
result = s_client.imageCensorUserDefined(get_file_content('images/12345678.jpg'))
print(result)










