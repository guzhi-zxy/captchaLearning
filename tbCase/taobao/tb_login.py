# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: tb_login.py
@time: 2020-06-16 17:50:07
@projectExplain:
"""

import asyncio
import random
from flask_restplus import Resource, reqparse, Namespace
import pyppdf.patch_pyppeteer
from pyppeteer import launch, launcher

api = Namespace('淘宝滑块验证')


@api.route('/', methods=['GET', 'POST'])
class TbTask(Resource):

    @api.doc(params={'url': 'slider url'})
    def post(self):

        req_parser = reqparse.RequestParser()
        req_parser.add_argument('url', type=str, required=True)
        args = req_parser.parse_args()

        url = args['url']
        print(url)
        if not url:
            return {
                'url': url,
                'x5sec': '',
            }
        try:
            # x5sec = asyncio.get_event_loop().run_until_complete(main(url))
            x5sec = asyncio.run(main(url))
            return {
                'x5sec': x5sec,
            }
        except:
            return {
                'url': url,
                'x5sec': '',
            }


def _save(cookies):
    x5sec = ''
    for cookie in cookies:
        if cookie.get('name') == 'x5sec':
            x5sec = cookie['value']
    return x5sec


async def main(url):
    print('=======')
    print(url)
    browser = await launch({
        'headless': False,
        'autoClose': True,
        # Running pypupeteer in FLASK gives ValueError: signal only works in main thread
        # need to call launch with disabled signals handling
        'handleSIGTERM': False,
        'handleSIGHUP': False,
        'handleSIGINT': False,
        'dumpio': True,
        'args': ['--no-sandbox',
                 '--disable-infobars',
                 '--disable-extensions',
                 '--hide-scrollbars',
                 '--disable-bundled-ppapi-flash',
                 '--mute-audio',
                 '--disable-setuid-sandbox',
                 '--disable-gpu',
                 '--log-level=30',
                 '--window-size=1366,768'],
    })
    page = await browser.newPage()
    print(page)
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
    await page.setViewport({'width': 1366, 'height': 768})

    await page.goto(url, {'waitUntil': 'networkidle2'})
    await page.evaluate("""
        () =>{
            Object.defineProperties(navigator,{
                webdriver:{
                get: () => false
                }
            })
        }
    """)
    await page.waitFor(3000)
    print('-------')
    cnt = 0
    while True:
        el = await page.J('#nc_1_n1z')
        box = await el.boundingBox()
        await page.hover('#nc_1_n1z')
        await page.mouse.down()
        await page.mouse.move(box['x'] + 258 + 29, box['y'], {'steps': 30})
        await page.waitFor(random.randint(300, 700))
        await page.mouse.move(box['x'] + 258 + 29, box['y'], {'steps': 30})
        await page.mouse.up()
        await page.waitFor(3000)
        cookies = await page.cookies()
        x5sec = _save(cookies)
        slide_refresh = await page.J('#nocaptcha > div > span > a')
        print('+++', slide_refresh)
        if slide_refresh:
            await page.click('#nocaptcha > div > span > a')
            await page.waitFor(300)
        else:
            break
        if cnt >= 10:
            break
        cnt += 1
        print(f'retry times ..≥{cnt}')

    return x5sec

