# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: __init__.py.py
@time: 2019-11-24 19:59:52
@projectExplain: 
"""

from flask import Blueprint
from flask_restplus import Api


blueprint = Blueprint('tbSlider', __name__, url_prefix='/tbSlider')
api = Api(blueprint)


from test.test_pc_slider import api as tb_slider_task
from test.test_app_slider import api as app_tb_slider_task
# from .tb_slider import api as tb_slider_task
# from .app_tb_slider import api as app_tb_slider_task
from .tb_login import api as app_tb_login

api.add_namespace(app_tb_login, path='/tb_slider')
api.add_namespace(tb_slider_task, path='/slider')
api.add_namespace(app_tb_slider_task, path='/app_slider')

