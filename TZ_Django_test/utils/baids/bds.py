import re
from aip import AipOcr, AipImageCensor


class Bd:
    def __init__(self):
        """ 你的 APPID AK SK """
        self.W_APP_ID = '18754614'
        self.API_KEY = 'a03533dabae3483a817d3faf7e244203'
        self.SECRET_KEY = '51b935e621884fd68912ffc012d8b4a8'

    def wz(self, image_file):
        client = AipOcr(self.W_APP_ID, self.API_KEY, self.SECRET_KEY)
        # image = get_file_content('example.jpg')
        data = client.basicGeneral(image_file)
        # data = str(data)
        # res = re.findall(r"{'words': '(.*?)'}", data)
        # print(res)
        print(data)
        for i in data['words_result']:
            print(i.get('words'))

    def jh(self, file_name):
        client = AipImageCensor(self.W_APP_ID, self.API_KEY, self.SECRET_KEY)
        res = client.imageCensorUserDefined(file_name)
        print(res)



if __name__ == '__main__':
    bd = Bd()
    with open('1.jpg', 'rb') as f:
        bd.wz(f.read())