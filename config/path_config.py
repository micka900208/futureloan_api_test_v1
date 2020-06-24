# -*- coding: utf-8 -*-
# @Time : 2020/6/9 22:22
# @Author : 深圳-烧烤-29期
# @File : path_config.py

import os
from futureloan_api_test_v1.common import yaml_handler

data=yaml_handler.read_yaml()

config_path=os.path.dirname(os.path.abspath(__file__))

root_path = os.path.dirname(config_path)


#测试用例路径
exl_path=os.path.join(root_path,data['excel']['file'])


#日志路径
logs_path=os.path.join(root_path,data['log']['file'])


#测试报告路径
repors_path = os.path.join(root_path,data['report']['file'])

#测试模块路径
test_path = os.path.join(root_path,'tests')


