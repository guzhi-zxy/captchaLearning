# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: wb_login.py
@time: 2020-07-20 12:22:06
@projectExplain: 微博登陆笔记
扣出微博登陆js后, 报错: execjs._exceptions.ProgramError: ReferenceError: navigator is not defined
解决办法: 初始化 navigator
var navigator = {};
"""

import re
import json
from urllib import parse
import execjs
import requests

html_str = ''
with open("./test3.js", 'r', encoding='utf-8') as f:
    for line in f:
        html_str += line
ctx = execjs.compile(html_str)  # 加载JS文件


def get_su(account):
    """
    获取加密参数su
    :param account: 传入账号
    :return:
    """
    account = parse.quote(account)
    su = ctx.call("_su", account)
    return su


def getkey(account):
    """
    获取加密需要的时间戳、公钥等信息
    :param account:
    :return:
    """
    su = get_su(account)
    su_url = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=" \
             "sinaSSOController.preloginCallBack&su={}%3D&rsakt" \
             "=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=1544491300471".format(su)
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "SINAGLOBAL=10.71.2.96_1537319283.25360; "
                  "UOR=www.baidu.com,news.sina.com.cn,; "
                  "SUB=_2AkMs_o_Sf8NxqwJRmfkVzWnma49-zgDEieKaon4JJRMyHR"
                  "l-yD9kql4ttRB6B36hPXoG3Dc1joQANXyggWcwbJoRDfhG; "
                  "SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhAxrOYgrYDalY30D0XuRdP;"
                  " ULV=1541659821773:4:1:1::1540805170207; "
                  "UM_distinctid=166f21629624c-036b343a4703ce-335e4b78-1fa400-166f216296327a; "
                  "lxlrttp=1541383354; U_TRS1=00000057.2c29756.5c0601f9.ec750a9c;"
                  " Apache=172.16.138.142_1544490894.221870",
        "Host": "login.sina.com.cn",
        "Referer": "https://www.weibo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 "
                      "Core/1.63.5603.400 QQBrowser/10.1.1775.400"
    }
    jsdata = requests.get(su_url, headers=headers)
    data = re.search('{.+}', jsdata.text).group()
    keys = json.loads(data)
    keys['su'] = su
    return keys


def login(account, password):
    """
    登陆程序
    :param account:
    :param password:
    :return: 登陆成功则返回用户信息json格式
    """
    keys = getkey(account)
    sp = ctx.call(
        "_sp", keys['pubkey'], keys['servertime'], keys['nonce'], password)
    data = {
        "entry": "weibo",
        "gateway": "1",
        "from": "",
        "savestate": "7",
        "qrcode_flag": "false",
        "useticket": "1",
        "pagerefer": "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r"
                     "=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
        "vsnf": "1",
        "su": keys['su'],
        "service": "miniblog",
        "servertime": keys['servertime'],
        "nonce": keys['nonce'],
        "pwencode": "rsa2",
        "rsakv": keys['rsakv'],
        "sp": sp,
        "sr": "1920*1080",
        "encoding": "UTF-8",
        "prelt": "44",
        "url": "https://www.weibo.com/ajaxlogin.php?framelogin=1&callback"
               "=parent.sinaSSOController.feedBackUrlCallBack",
        "returntype": "META"
    }

    r = requests.Session()
    log_url = 'https://login.sina.com.cn/sso/' \
              'login.php?client=ssologin.js(v1.4.19)'
    page = r.post(log_url, data=data)
    """被重定向两次"""
    page.encoding = "GBK"
    url = re.search('location\.replace\([\'"](.*?)[\'"]\)', page.text).group(1)
    page = r.post(url, data=data)
    page.encoding = "GBK"
    url = re.search('location\.replace\([\'"](.*?)[\'"]\)', page.text).group(1)
    page = r.post(url, data=data)
    print(page.cookies)
    print(requests.utils.dict_from_cookiejar(page.cookies))
    params = (
        ('customer_id', '6135567862'),
        ('startTime', '2020-07-19'),
        ('endTime', '2020-07-19'),
        ('field[]', ['consume', 'pv', 'traffic_bhv', 'traffic_bhv_rate', 'ecpm', 'traffic_bhv_cost']),
        ('granularity[]', ['account', 'date']),
        ('dimension[]', 'account'),
        ('orderBy[]', 'date'),
        ('orderMode', 'desc'),
        ('rows', '10'),
        ('page', '1'),
        ('tableType', 'effect'),
        ('mergeType', 'normal'),
        ('summary[]', ['avg', 'sum']),
        ('fans', '1'),
    )
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://ad.weibo.com/data/index?customer_id=6135567862',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    res = r.get(url='https://ad.weibo.com/aj/data/getEffectTable', params=params, headers=headers,
                cookies=page.cookies, verify=False).json()
    print(res)
    return res


if __name__ == '__main__':
    login('account', 'password')
