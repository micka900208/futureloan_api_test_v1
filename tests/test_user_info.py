# -*- coding: utf-8 -*-
# @Time : 2020/6/13 17:22
# @Author : 深圳-烧烤-29期
# @File : test_user_info.py

import json
import unittest
from ddt import ddt, data
from common import request_handler
from middleware import handler

# 实例一个日志收集器
logger = handler.ConfHandler.logger

# 初始化handler
env_data = handler.ConfHandler()

# 调用配置文件解析模块
test_data = env_data.exl_handler.read_data(env_data.info_sheet)


@ddt
class TestGetInfo(unittest.TestCase):
    def setUp(self):
        self.exl = env_data.exl_handler

    @data(*test_data)
    def test_get_info(self, data_info):
        global TestResult
        logger.info('******************正在执行user_info模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))
        # 拼接请求地址url
        url = "".join([env_data.host,data_info['url']])
        res = request_handler.visit(url,
                                    method=data_info['method'],
                                    headers=json.loads(data_info['headers']))
        try:
            for k, v in eval(data_info['expected']).items():
                self.assertTrue(v == res[k])
            TestResult = 'PASS'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], TestResult))
        except AssertionError as e:
            logger.error("执行接口测试出现错误，错误是{}".format(e))
            TestResult = 'FAILED'
            logger.error("第{}条用例执行结果为{}".format(data_info['case_id'], TestResult))
        finally:
            logger.info('*************开始回写数据***************')
            self.exl.write_excel(env_data.info_sheet, data_info['case_id'] + 1, 9, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            self.exl.write_excel(env_data.info_sheet, data_info['case_id'] + 1, 10, TestResult)
            logger.info('正在回写测试结果test_result：{}'.format(TestResult))
            logger.info('*************结束回写数据***************')


if __name__ == '__main__':
    unittest.main()
