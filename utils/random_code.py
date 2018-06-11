import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class Captcha(object):
    """
    生成随机验证码
    """
    def __init__(self, font_url, font_size=36, image_size=(120, 80)):
        self.font = ImageFont.truetype(font_url, font_size)
        self.image = Image.new(mode='RGB', size=image_size, color=self.rand_color())
        self.draw = ImageDraw.Draw(self.image)

    def rand_color(self):
        """
        :return: 生成随机颜色
        """
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return color

    def get_rand_code(self, num=5, x=20, y=26, ):
        """
        此方法生成随机字符串(字母+数字)
        :param num: 生成字符个数
        :param x: 字符间隔(x坐标)
        :param y: 图像y坐标轴
        :return: 返回随机验证码
        """
        temp = []
        for i in range(num):
            random_char = random.choice([
                str(random.randint(0, 9)),
                chr(random.randint(65, 90)),
                chr(random.randint(97, 122))
            ])
            temp.append(random_char)
            self.draw.text((i * x, y), random_char, self.rand_color(), font=self.font)
        return ''.join(temp)

    def get_image(self):
        """
        :return: 返回写入随机字符的图像
        """
        f = BytesIO()  # 用于存储生成图像的内存缓冲区。
        self.image.save(f, "png")  # 把图像保存到内存
        data = f.getvalue()  # 从内存缓冲区提取图像
        return data















