# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: mitmproxy.py
@time: 2020-03-25 09:49:14
@projectExplain: 
"""
'''
import json
from urllib.parse import urlparse
from mitmproxy import http

# INJECT_TEXT = 'Object.defineProperties(navigator,{webdriver:{get:() => false}});' #js执行文件

def response(flow: http.HTTPFlow):
    # if 'index' in flow.request.url:
    #     flow.response.text = INJECT_TEXT + flow.response.text
    #     print('注入成功')
    response = flow.response
    # 获取响应内容
    content = response.content
    # print(content)
    # log = ctx.log

    tmp = urlparse(flow.request.url)
    print('++++', tmp)
    # if '/slide/g.html' == str(tmp.path):
    #     res = json.loads(content.decode())
    #     with open('ro.txt', 'w') as fw:
            # fw.write(res)
'''
import re
from mitmproxy import ctx

INJECT_TEXT = 'Object.defineProperties(navigator,{webdriver:{get:() => false}});' #js执行文件


def response(flow):
    if "/_next/static/js/common_pdd" in flow.request.url:
        flow.response.text = flow.response.text.replace("webdriver", "userAgent")
    if '/js/yoda.' in flow.request.url:
        for webdriver_key in ['webdriver', '__driver_evaluate', '__webdriver_evaluate', '__selenium_evaluate',
                              '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped',
                              '__selenium_unwrapped', '__fxdriver_unwrapped', '_Selenium_IDE_Recorder', '_selenium',
                              'calledSelenium', '_WEBDRIVER_ELEM_CACHE', 'ChromeDriverw', 'driver-evaluate',
                              'webdriver-evaluate', 'selenium-evaluate', 'webdriverCommand',
                              'webdriver-evaluate-response', '__webdriverFunc', '__webdriver_script_fn',
                              '__$webdriverAsyncExecutor', '__lastWatirAlert', '__lastWatirConfirm',
                              '__lastWatirPrompt', '$chrome_asyncScriptInfo', '$cdc_asdjflasutopfhvcZLmcfl_']:
            ctx.log.info('Remove "{}" from {}.'.format(
                webdriver_key, flow.request.url
            ))
        flow.response.text = flow.response.text.replace('"{}"'.format(webdriver_key), '"NO-SUCH-ATTR"')
    flow.response.text = flow.response.text.replace('t.webdriver', 'false')
    flow.response.text = flow.response.text.replace('ChromeDriver', '')

