# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: tb_slider.py
@time: 2019-11-24 19:13:48
@projectExplain:
"""

import time
import random
from flask_restplus import Resource, reqparse, Namespace

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

api = Namespace('淘宝滑块验证')


@api.route('/', methods=['GET', 'POST'])
class TbTask(Resource):

    @api.doc(params={'url': 'slider url'})
    def post(self):

        req_parser = reqparse.RequestParser()
        req_parser.add_argument('url', type=str, required=True)
        args = req_parser.parse_args()

        url = args['url']
        if not url:
            return {
                'url': url,
                'x5sec': '',
            }

        option = ChromeOptions()
        # option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')

        option.add_argument('--disable-extensions')
        option.add_argument('--disable-gpu')
        option.add_argument("--disable-features=VizDisplayCompositor")
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option("useAutomationExtension", False)
        option.binary_location = '/root/Downloads/login_taobao/node_modules/puppeteer/.local-chromium/linux-672088/chrome-linux/chrome'
        wd = Chrome(options=option, executable_path='/root/Downloads/slider_servers/chromedriver')
        # wd = Chrome(ChromeDriverManager().install(), options=option)
        wd.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        '''
        wd.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                               Object.defineProperty(navigator, 'webdriver', {
                                 get: () => undefined
                               });
                               Object.defineProperty(navigator, 'language', {
	                             get: () => "zh-CN"
                               });
                               Object.defineProperty(navigator, 'deviceMemory', {
	                             get: () => 8
                               });
                               Object.defineProperty(navigator, 'hardwareConcurrency', {
	                             get: () => 8
                               });
                               Object.defineProperty(navigator, 'platform', {
	                             get: () => 'MacIntel'
                               });
                               Object.defineProperty(navigator, 'userAgent', {
                                 get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
                               });
                               Object.defineProperty(navigator, 'plugins', {
                                 get: () => [1, 2, 3, 4, 5]
                               });
                             """
        })
        '''
        wd.set_page_load_timeout(20)
        _timeout = WebDriverWait(wd, 20)
        try:
            x5sec = ''
            wd.get(url)
            wd.implicitly_wait(10)
            wd.delete_all_cookies()
            cnt = 0
            while True:
                time.sleep(0.4)
                wd.find_element_by_id("nc_1_n1z").click()
                slid_ing = wd.find_element_by_id("nc_1_n1z")
                ActionChains(wd).click_and_hold(on_element=slid_ing).perform()
                time.sleep(0.2)
                lgh = 0
                try:
                    while lgh <= 510:
                        lgh += random.randint(30, 50)
                        ActionChains(wd).move_by_offset(xoffset=lgh, yoffset=0).perform()
                    time.sleep(0.2)
                    #ActionChains(wd).move_by_offset(xoffset=258, yoffset=0).perform()
                    ActionChains(wd).release().perform()

                except:
                    time.sleep(0.4)
                    ActionChains(wd).release().perform()
                try:
                    slide_refresh = wd.find_element_by_xpath("//div[@id='nocaptcha']/div/span/a")
                    slide_refresh.click()
                except:
                    break
                cnt += 1
                if cnt > 10:
                    break
            cookies = wd.get_cookies()
            wd.close()
            for x5sec_data in cookies:
                if 'x5sec' in x5sec_data.values():
                    x5sec = x5sec_data['value']
            return {
                'x5sec': x5sec,
            }
        except:
            wd.close()
            return {
                'url': url,
                'x5sec': '',
            }
