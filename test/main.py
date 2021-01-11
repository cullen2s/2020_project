# coding:utf-8
import os
import re, requests
from bs4 import BeautifulSoup

from PIL import Image
from io import BytesIO

s = requests.session()  # 保留会话


def re_test(text):
    '''
    :param text: 网页源文件
    :return: 返回图片的链接
    '''
    # https://imgsa.baidu.com/forum/w%3D580/sign=20bec30aa0ec8a13141a57e8c7029157/2508562c11dfa9ecfd81b1f26bd0f703938fc180.jpg
    img_url = re.findall('https://imgsa.baidu.com/forum/.*?jpg', text)
    return img_url


def bs_test(text):
    '''
    :param text: 网页源文件
    :return: 返回图片的链接
    '''
    # <img class="BDE_Image" src="https://imgsa.baidu.com/forum/w%3D580/sign=44312fe1a5af2eddd4f149e1bd110102/1c3477094b36acaf1ce5c71b75d98d1000e99c2f.jpg" size="201260" width="479" height="852">
    soup = BeautifulSoup(text, "lxml")
    img_urls = soup.find_all('img', {'class': 'BDE_Image'})
    img_url = [i.get('src') for i in img_urls]
    return img_url


class ImageUtils(object):
    @staticmethod
    def image_compose(imgDir, picWidth, picHigh, savePath, row=1, column=1):
        '''
        :param imgDir: 图片路径
        :param picWidth: 缩放图宽带
        :param picHigh: 缩放图高度
        :param savePath: 保存路径
        :param row: x 行
        :param column: x 列
        :return:
        '''
        IMAGES_FORMAT = ['.png', '.PNG', '.jpg', ".JPG"]  # 图片格式
        # 获取图片集地址下的所有图片名称
        image_names = [name for name in os.listdir(imgDir) for item in IMAGES_FORMAT if
                       os.path.splitext(name)[1] == item]
        # 定义图像拼接函数
        to_image = Image.new('RGB', (column * picWidth, row * picHigh))  # 创建一个新图
        # 循环遍历，把每张图片按顺序粘贴到对应位置上

        for y in range(1, row + 1):
            for x in range(1, column + 1):
                if column * (y - 1) + x - 1 > len(image_names) - 1:
                    from_image = Image.new('RGB', (picWidth, picHigh), (255, 255, 255))
                else:
                    from_image = Image.open(imgDir + image_names[column * (y - 1) + x - 1]).resize(
                        (picWidth, picHigh), Image.ANTIALIAS)
                to_image.paste(from_image, ((x - 1) * picWidth, (y - 1) * picHigh))

        return to_image.save(savePath)  # 保存新图


def img_size(content):
    img = Image.open(BytesIO(content))
    return img.size


def save_img(url):
    img_name = url.strip().split('/')[-1]
    print(img_name)
    url_re = s.get(url.strip())
    if url_re.status_code == 200:  # 200是http响应状态
        # print('准备保存')
        if not os.path.exists('pictures'):  # 没有文件夹，则创建文件夹
            os.mkdir('pictures')
        if img_size(url_re.content)[0] > 400 and img_size(url_re.content)[1] > 600:  # 图片宽*高大于400*600像素才保存
            print('保存')
            open('pictures/' + img_name, 'wb').write(url_re.content)


if __name__ == '__main__':
    for i in range(3):  #获取前三页
        url = 'https://tieba.baidu.com/p/5033202671?pn=' + str(i + 1)  # 构造和Page相关的链接
        print(url)
        req_text = s.get(url).text
        # print(re_test(req_text)) # 正则
        # urls = re_test(req_text)
        # print(bs_test(req_text)) # BS
        urls = bs_test(req_text)
        for img_url in re_test(req_text):  # 采用正则获取图片链接
            save_img(img_url)

    ImageUtils.image_compose(os.getcwd() + "/pictures/", 360, 640, 'res.jpg', 4, 5)
