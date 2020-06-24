# -*- coding: utf-8 -*-
# @Time : 2020/6/8 21:51
# @Author : 深圳-烧烤-29期
# @File : homework_0606_shaokao.py

"""接口请求访问"""

import requests

"""函数封装requests"""

def visit(
        url,
        method='get',
        params=None,
        data=None,
        json=None,
        **kwargs
):
    res = requests.request(method,
                           url,
                           params=params,
                           data=data,
                           json=json,
                           **kwargs)
    return res.json()



