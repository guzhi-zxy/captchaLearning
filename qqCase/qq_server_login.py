# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: qq_server_login.py
@time: 2020-07-17 09:55:52
@projectExplain: 
"""

# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: gdt_login.py
@time: 2019-11-25 15:14:27
@projectExplain:
"""

import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import time
import random
import json
import requests
from redis import StrictRedis
from PIL import Image

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from qqCase.gdt_crack import qq_mark_detect

dd_token_url = 'xxx'


def dd_notice(content, token_url=dd_token_url):
    """
    钉钉机器人
    """
    content = "{}".format(content)
    data = {
        "msgtype": "text",
        "text": {
            "content": f'{content}',
        },
    }
    data = json.dumps(data)
    h = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.post(token_url, headers=h, data=data, verify=False)
    return r.text


class S(object):
    def __init__(self):
        self.path = '/root/.wdm/drivers/chromedriver/80.0.3987.106/linux64/chromedriver'
        option = ChromeOptions()
        option.add_argument('--headless')
        prefs = {
            'profile.default_content_setting_values': {
                'notifications': 2
            }
        }
        option.add_experimental_option('prefs', prefs)
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--disable-extensions')
        option.add_argument('--disable-gpu')
        option.add_argument("--disable-features=VizDisplayCompositor")
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.wd = Chrome(options=option, executable_path=self.path)
        # 移除webdriver
        self.wd.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                           Object.defineProperty(navigator, 'webdriver', {
                             get: () => undefined
                           })
                         """
        })
        self.wd.set_page_load_timeout(20)
        self.timeout = WebDriverWait(self.wd, 20)
        self.url = 'https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101477621&redirect_uri=https%3A%2F%2Fsso.e.qq.com%2Fpassport%3Fsso_redirect_uri%3Dhttps%253A%252F%252Fe.qq.com%252Fads%252F%26service_tag%3D1&scope=get_user_info'
        self.users = 'xxx'
        self.passwd = 'xxx'

    def run(self):
        self.wd.get(self.url)
        self.wd.implicitly_wait(10)
        self.wd.delete_all_cookies()
        time.sleep(2)

        iframe = self.wd.find_element_by_xpath('//iframe')
        self.wd.switch_to.frame(iframe)

        self.wd.find_element_by_id('switcher_plogin').click()
        time.sleep(1)
        self.wd.find_element_by_id('u').clear()
        time.sleep(1)
        self.wd.find_element_by_id('u').send_keys(self.users)
        time.sleep(2)
        self.wd.find_element_by_id('p').clear()
        time.sleep(1)
        self.wd.find_element_by_id('p').send_keys(self.passwd)
        time.sleep(2)
        self.wd.find_element_by_id('login_button').click()
        time.sleep(5)
        try:
            tips = self.wd.find_element_by_id('qlogin_tips_2').text
            if '由于你的帐号存在异常，需要进行手机验证，' in tips:
                while True:
                    dd_notice('需要扫描二维码...', dd_token_url)
                    time.sleep(2)
                    self.wd.save_screenshot('qrImg.png')
                    im = Image.open('qrImg.png')
                    im.save('qrImg.png')
                    time.sleep(30)
                    requests.get('https://e.qq.com/atlas/8944022/admanage/campaign', verify=False)
                    time.sleep(2)
                    if 'gdt_token' in json.dumps(self.wd.get_cookies()):
                        dd_notice('二维码验证成功！！！', dd_token_url)
                        break
                    else:
                        dd_notice('二维码验证失败！重试中...', dd_token_url)
        except Exception as e:
            dd_notice('不需要二维码验证！', dd_token_url)

        try:
            while True:
                time.sleep(3)
                iframe = self.wd.find_element_by_xpath('//iframe')
                self.wd.switch_to.frame(iframe)
                time.sleep(1)
                flags = self.wd.find_element_by_xpath('//*[@id="guideText"]').text
                if '拖动下方滑块完成拼图' == flags:
                    dd_notice('需要滑块！！！', dd_token_url)
                    src_url = self.wd.find_element_by_xpath('//*[@id="slideBg"]').get_attribute('src')
                    res = requests.get(url=src_url, verify=False)
                    with open('crack.jpeg', 'wb') as f:
                        f.write(res.content)
                    time.sleep(3)
                    slid_ing = self.wd.find_element_by_id('tcaptcha_drag_button')
                    ActionChains(self.wd).click_and_hold(on_element=slid_ing).perform()
                    time.sleep(0.2)
                    position = qq_mark_detect('crack.jpeg').x.values[0]
                    real_position = position * (280 / 680) - 23
                    track_list = self.get_track(int(real_position))
                    for track in track_list:
                        ActionChains(self.wd).move_by_offset(xoffset=track, yoffset=0).perform()
                        time.sleep(0.002)
                    ActionChains(self.wd).release().perform()
                    time.sleep(2)
                    requests.get('https://e.qq.com/atlas/8944022/admanage/campaign', verify=False)
                    time.sleep(2)
                    print(self.wd.get_cookies())
                    if 'gdt_token' in json.dumps(self.wd.get_cookies()):
                        dd_notice('滑块验证成功！！！', dd_token_url)
                        break
                    else:
                        dd_notice('滑块验证验证失败！重试中...', dd_token_url)
                else:
                    dd_notice('不需要滑块！！！', dd_token_url)
        except Exception as e:
            dd_notice('不需要滑块！', dd_token_url)
        cookies_data = self.wd.get_cookies()
        try:
            if 'gdt_token' in json.dumps(cookies_data) and 'gdt_protect' in json.dumps(cookies_data):
                cookies = {}
                for data in cookies_data:
                    if 'gdt_protect' in data.values():
                        gdt_protect = data.get('value')
                        if gdt_protect:
                            cookies['gdt_protect'] = gdt_protect
                    if 'gdt_token' in data.values():
                        gdt_token = data.get('value')
                        if gdt_token:
                            cookies['gdt_token'] = gdt_token
                dd_notice(f'获取的cookies: {cookies}', dd_token_url)
                time.sleep(2)
                self.close()
            else:
                dd_notice('未成功获取cookies, 需手动重试!!!!!', dd_token_url)
                self.close()
        except Exception as e:
            dd_notice('广点通自动化登陆失败！！！需手动重试!!!!!', dd_token_url)
            self.close()

    @staticmethod
    def get_track(distance):
        """
        模拟轨迹 假装是人在操作
        :param distance:
        :return:
        """
        v = 0
        t = 0.2
        tracks = []
        current = 0
        mid = distance * 7 / 8

        distance += 10
        while current < distance:
            if current < mid:
                a = random.randint(2, 4)
            else:
                a = -random.randint(3, 5)

            v0 = v
            s = v0 * t + 0.5 * a * (t ** 2)
            current += s
            tracks.append(round(s))

            v = v0 + a * t

        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks

    def close(self):
        self.wd.close()


if __name__ == '__main__':
    S().run()
