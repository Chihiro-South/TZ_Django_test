from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.services.bos.bos_client import BosClient
class Bd_Storage(object):
    def __init__(self):
        self.bos_host = "http://bos.bj.baidubce.com"
        self.access_key_id = ""
        self.secret_access_key = ""
        self.back_name = ''

    def up_image(self,file):
        config = BceClientConfiguration(credentials=BceCredentials(self.access_key_id,self.secret_access_key),endpoint=self.bos_host)
        client = BosClient(config)
        self.key_name = '1234.jpg'
        try:
            res = client.put_object_from_string(bucket=self.back_name, key=self.key_name, data=file)
        except Exception as e:
            raise e
        else:
            result = res.__dict__
            if result['metadata']:
                url = 'https://' + self.back_name + '.bj.bcebos.com/'+ self.key_name
                print('图片上传成功')
                return url


if __name__ == '__main__':
    bd = Bd_Storage()
    with open('wyz.jpg', 'rb') as f:
        s = f.read()
        bd.up_image(s)