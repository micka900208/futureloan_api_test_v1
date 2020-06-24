# -*- coding: utf-8 -*-
# @Time : 2020/6/11 22:42
# @Author : 深圳-烧烤-29期
# @File : test_login.py

import unittest
from ddt import ddt, data
from futureloan_api_test_v1.common import request_handler
from futureloan_api_test_v1.middleware import handler

# 实例一个日志收集器
logger = handler.ConfHandler.logger

# 初始化handler
env_data = handler.ConfHandler()

# 调用配置文件解析模块
test_data = env_data.exl_handler.read_data(env_data.login_sheet)


@ddt
class TestLogin(unittest.TestCase):
    def setUp(self):
        self.exl = env_data.exl_handler

    @data(*test_data)
    def test_login(self, data_info):
        global TestResult
        logger.info('******************正在执行login模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))
        # 请求地址拼接
        url = "".join([env_data.host, data_info['url']])
        res = request_handler.visit(url,
                                    method=data_info['method'],
                                    json=eval(data_info['data']),
                                    headers=eval(data_info['headers']))
        try:
            # 预期结果与返回结果比对
            for k, v in eval(data_info['expected']).items():
                self.assertTrue(v == res[k])
            # 若断言成功，则测试结果为pass
            TestResult = 'PASS'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], TestResult))
        except AssertionError as e:
            logger.info("执行接口测试出现错误，错误是{}".format(e))
            # 若断言成功，则测试结果为failed
            TestResult = 'FAILED'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], TestResult))
        finally:
            logger.info('*************开始回写数据***************')
            # 实际结果进行回写
            self.exl.write_excel(handler.ConfHandler.login_sheet, data_info['case_id'] + 1, 9, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            # 测试结果进行回写
            self.exl.write_excel(handler.ConfHandler.login_sheet, data_info['case_id'] + 1, 10, TestResult)
            logger.info('正在回写测试结果test_result：{}'.format(TestResult))
            logger.info('*************结束回写数据***************')


if __name__ == '__main__':
    unittest.main()
