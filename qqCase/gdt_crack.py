# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: gdt_login.py
@time: 2019-11-25 15:14:27
@projectExplain:
"""

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


def get_dx_median(dx, x, y, w, h):
    return np.median(dx[y:(y + h), x])


def pre_process(image):
    img = cv2.imread(image, 1)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    dx = cv2.Sobel(img, -1, 1, 0, ksize=5)

    ret, binary = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    gray = np.zeros_like(img_gray)
    cv2.drawContours(gray, contours, -1, (0, 0, 255), thickness=1)

    rect_area = []
    rect_arclength = []
    cnt_infos = {}

    colors = plt.cm.Spectral(np.linspace(0, 1, len(contours)))

    for i, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < 5000 or cv2.contourArea(cnt) > 25000:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        cnt_infos[i] = {'rect_area': w * h,
                        'rect_arclength': 2 * (w + h),
                        'cnt_area': cv2.contourArea(cnt),
                        'cnt_arclength': cv2.arcLength(cnt, True),
                        'cnt': cnt,
                        'w': w,
                        'h': h,
                        'x': x,
                        'y': y,
                        'mean': np.mean(np.min(img[y:(y + h), x:(x + w)], axis=2)),
                        }
        rect_area.append(w * h)
        rect_arclength.append(2 * (w + h))

        cv2.rectangle(img, (x, y), (x + w, y + h), colors[i], 1)

    return img, dx, cnt_infos


def qq_mark_detect(image):
    img, dx, cnt_infos = pre_process(image)
    h, w = img.shape[:2]
    df = pd.DataFrame(cnt_infos).T
    df.head()
    df['dx_mean'] = df.apply(lambda x: get_dx_median(dx, x['x'], x['y'], x['w'], x['h']), axis=1)
    df['rect_ratio'] = df.apply(lambda v: v['rect_arclength'] / 4 / math.sqrt(v['rect_area'] + 1), axis=1)
    df['area_ratio'] = df.apply(lambda v: v['rect_area'] / v['cnt_area'], axis=1)
    df['score'] = df.apply(lambda x: abs(x['rect_ratio'] - 1), axis=1)
    result = df.query('x>0').query('area_ratio<2').query('rect_area>5000').query('rect_area<20000').sort_values(
        ['mean', 'score', 'dx_mean']).head(2)
    if len(result):
        x_left = result.x.values[0]
        cv2.line(img, (x_left, 0), (x_left, h), color=(255, 0, 255))

    return result


if __name__ == "__main__":
    image = "qq_max.jpeg"
    res = qq_mark_detect(image)
    print(res.x.values[0])
