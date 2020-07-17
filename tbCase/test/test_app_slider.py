# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: test_app_slider.py
@time: 2020-05-29 14:40:35
@projectExplain: 
"""


import time
import random
from flask_restplus import Resource, reqparse, Namespace

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
# from libs.utils import log_access, error_handler
# from libs.log import get_logger
#
# log = get_logger('tb_slider')


import string
import zipfile
from selenium import webdriver

# 代理服务器（ip+port）
proxyHost = "ip"
proxyPort = "port"
# 代理隧道验证信息（账号+密码）
proxyUser = "user"
proxyPass = "password"

api = Namespace('淘宝滑块验证')


@api.route('/', methods=['GET', 'POST'])
class TbTask(Resource):

    # @log_access
    # @error_handler
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
        # option.add_argument('--proxy-server=http://HD3P6R2K3912I09D:01EFD204EBDD30EB@http-dyn.abuyun.com:9020')
        mobile_emulation = {"deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 3},
                            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372"}
        option.add_experimental_option("mobileEmulation", mobile_emulation)
        option.add_experimental_option('w3c', False)
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--disable-extensions')
        option.add_argument('--disable-gpu')
        option.add_argument("--disable-features=VizDisplayCompositor")
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option("useAutomationExtension", False)
        # option.binary_location = '/root/Downloads/login_taobao/node_modules/puppeteer/.local-chromium/linux-672088/chrome-linux/chrome'
        wd = Chrome(options=option, executable_path='chromedriver')
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
                wd.find_element_by_id("nc_1_n1t").click()
                slid_ing = wd.find_element_by_id("nc_1_n1t")
                time.sleep(0.2)
                try:
                    # TouchActions(wd).flick_element(slid_ing, 258, 0, random.randint(200, 300)).perform()
                    TouchActions(wd).flick_element(slid_ing, 258, 0, 358).perform()
                    time.sleep(0.4)
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    print(e)
                    time.sleep(0.4)
                try:
                    slide_refresh = wd.find_element_by_xpath('//*[@id="nc_1-stage-3"]/span[1]/span[1]')
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
