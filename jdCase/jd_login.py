# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: jd_login.py
@time: 2020-03-24 20:14:25
@projectExplain: 
"""
import base64
import random
from time import sleep
import cv2
from selenium.webdriver.support.ui import WebDriverWait
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from matplotlib.font_manager import FontProperties
from pylab import array, imshow, ginput, show, axis
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

USERNAME = "xxx"
PASSWORD = "xxx"


def get_track7(distance):
    """
    根据偏移量和手动操作模拟计算移动轨迹
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    tracks = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 时间间隔
    t = 0.2
    # 初始速度
    v = 0

    while current < distance:
        if current < mid:
            a = random.uniform(2, 5)
        else:
            a = -(random.uniform(12.5, 13.5))
        v0 = v
        v = v0 + a * t
        x = v0 * t + 1 / 2 * a * t * t
        current += x

        if 0.6 < current - distance < 1:
            x = x - 0.53
            tracks.append(round(x, 2))

        elif 1 < current - distance < 1.5:
            x = x - 1.4
            tracks.append(round(x, 2))
        elif 1.5 < current - distance < 3:
            x = x - 1.8
            tracks.append(round(x, 2))

        else:
            tracks.append(round(x, 2))

    print(sum(tracks))
    return tracks


def get_grap():
    """用opencv识别缺口位置"""
    otemp = 'patch.png'
    oblk = 'bg.png'
    target = cv2.imread(otemp, 0)
    template = cv2.imread(oblk, 0)
    w, h = target.shape[::-1]
    temp = 'temp.jpg'
    targ = 'targ.jpg'
    cv2.imwrite(temp, template)
    cv2.imwrite(targ, target)
    target = cv2.imread(targ)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    target = abs(255 - target)
    cv2.imwrite(targ, target)
    target = cv2.imread(targ)
    template = cv2.imread(temp)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    y, x = np.unravel_index(result.argmax(), result.shape)
    # 展示圈出来的区域
    cv2.rectangle(template, (x, y), (x + w, y + h), (7, 249, 151), 1)
    plt.imshow(template)
    plt.show()
    print('缺口偏移量：', x)
    if x < 100:
        x = x * (272 / 360) + 24
    elif x < 180:
        x = x * (272 / 360) + 28
    else:
        x = x * (272 / 360) + 32
    return x


class jdLogin(object):
    def __init__(self):
        self.path = './chromedriver'

        option = ChromeOptions()
        # option.add_argument('--headless')
        prefs = {
            'profile.default_content_setting_values': {
                'notifications': 2
            }
        }
        option.add_experimental_option('prefs', prefs)
        option.add_argument('--no-sandbox')
        option.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36')
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--disable-extensions')
        option.add_argument('--disable-gpu')
        # option.add_argument('--proxy-server=http://127.0.0.1:8080')
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = Chrome(options=option, executable_path=self.path)

        # 反检测
        # 移除webdriver
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })

        self.driver.set_page_load_timeout(30)
        self.timeout = WebDriverWait(self.driver, 30)
        # self.driver.set_window_size(1920, 1080)


    def get_login(self):
        self.driver.get('http://passport.jd.com/new/login.aspx')
        self.driver.find_element_by_xpath('//a[@clstag="pageclick|keycount|login_pc_201804112|10"]').click()
        sleep(0.5)
        self.driver.find_element_by_id('loginname').send_keys(USERNAME)
        sleep(0.5)
        self.driver.find_element_by_id('nloginpwd').send_keys(PASSWORD)
        sleep(0.5)
        self.driver.find_element_by_id('loginsubmit').click()


    def download_imgs(self):
        bgData = self.driver.find_element_by_xpath('//div[@class="JDJRV-bigimg"]/img').get_attribute('src')
        bg = bgData.split('base64,')[1]
        patchData = self.driver.find_element_by_xpath('//div[@class="JDJRV-smallimg"]/img').get_attribute('src')
        patch = patchData.split('base64,')[1]
        bgData = base64.b64decode(bg)
        with open('bg.png', 'wb') as fw1:
            fw1.write(bgData)
        patchData = base64.b64decode(patch)
        with open('patch.png', 'wb') as fw2:
            fw2.write(patchData)

    def dragging(self, tracks):
        # 按照行动轨迹先正向滑动，后反滑动
        button = self.driver.find_element_by_class_name('JDJRV-slide-btn')
        ActionChains(self.driver).click_and_hold(button).perform()
        tracks_backs = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]  # -20

        for track in tracks:
            ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()

        # sleep(0.08)
        # 反向滑动
        # for back in tracks_backs:
        #      ActionChains(self.dr).move_by_offset(xoffset=back, yoffset=0).perform()

        ActionChains(self.driver).move_by_offset(xoffset=-3, yoffset=0).perform()
        ActionChains(self.driver).move_by_offset(xoffset=3, yoffset=0).perform()

        sleep(0.7)
        ActionChains(self.driver).release().perform()
        print('stop...')

    def main(self):
        self.get_login()  # 访问登录页，选择密码登陆
        sleep(1)
        slide = self.driver.find_element_by_class_name("JDJRV-suspend-slide")
        if slide:
            print("进入滑块验证码流程")
            self.download_imgs()
            sleep(1)
            move = get_grap()
            # track = get_track7(move + 20.85)
            track = get_track7(move -2.5)
            self.dragging(track)
            sleep(100)


if __name__ == '__main__':
    jdLogin().main()
    # get_grap()

