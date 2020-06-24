# -*- coding: utf-8 -*-
# @Time : 2020/5/30 16:28
# @Author : 深圳-烧烤-29期
# @File : yaml_handler.py

"""配置文件读取"""

import yaml, os

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
yml_path = os.path.join(path, 'config', 'config.yaml')


def read_yaml():
    with open(yml_path, 'r', encoding='utf-8') as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)
    return conf


def write_yaml(data):
    with open(yml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)
