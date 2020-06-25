# -*- coding: utf-8 -*-
# @Time : 2020/5/30 16:16
# @Author : 深圳-烧烤-29期
# @File : run_test.py

import unittest, HTMLTestRunnerNew
from config import path_config
from middleware import handler


# 初始化handler
env_data = handler.ConfHandler()

def test_report():
    with open(env_data.rpt_file, 'wb+') as f:
        loader = unittest.TestLoader()
        suite = loader.discover(path_config.test_path)
        runner = HTMLTestRunnerNew.HTMLTestRunner(
            f,
            2,
            title=env_data.rpt_conf['title'],
            description=env_data.rpt_conf['description'],
            tester=env_data.rpt_conf['tester']
        )
        runner.run(suite)


if __name__ == '__main__':
    test_report()

