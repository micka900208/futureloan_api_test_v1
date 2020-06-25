# -*- coding: utf-8 -*-
# @Time : 2020/6/13 16:43
# @Author : 深圳-烧烤-29期
# @File : test_update_name.py
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
test_data = env_data.exl_handler.read_data(env_data.update_sheet)


@ddt
class TestUpdateName(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.token = env_data.token
        cls.member_id = env_data.member_id

    def setUp(self):
        self.exl = env_data.exl_handler
        self.db = env_data.db_class()

    def tearDown(self) -> None:
        self.db.close()

    @data(*test_data)
    def test_update_name(self, data_info):
        global TestResult

        # 登录获取的memberid替换掉excel的member_id
        if "#id#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#id#", str(self.member_id))
        # 登录获取的token替换掉excel的token
        if "#token#" in data_info["headers"]:
            data_info["headers"] = data_info["headers"].replace("#token#", self.token)

        logger.info('******************正在执行update模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))
        # 拼接请求地址url
        url = "".join([env_data.host, data_info['url']])
        res = request_handler.visit(url,
                                    method=data_info['method'],
                                    json=json.loads(data_info['data']),
                                    headers=json.loads(data_info['headers']))
        try:
            for k, v in eval(data_info['expected']).items():
                self.assertTrue(v == res[k])
            if res['code'] == 0:
                logger.info("======================正在查询修改后的用户昵称=======================")
                sql_1 = "select reg_name from member where id = {};".format(self.member_id)
                after_data = self.db.query(sql_1)
                after_name = after_data['reg_name']
                logger.info("账户id为{}的昵称修改后为{}".format(self.member_id, after_name))
                # 比对修改成功后昵称是否修改正确
                logger.info("======================正在昵称信息比对比对=======================")
                self.assertTrue(after_name == json.loads(data_info['data'])['reg_name'])
            TestResult = 'PASS'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], TestResult))
        except AssertionError as e:
            logger.error("执行接口测试出现错误，错误是{}".format(e))
            TestResult = 'FAILED'
            logger.error("第{}条用例执行结果为{}".format(data_info['case_id'], TestResult))
        finally:
            logger.info('*************开始回写数据***************')
            self.exl.write_excel(env_data.update_sheet, data_info['case_id'] + 1, 9, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            self.exl.write_excel(env_data.update_sheet, data_info['case_id'] + 1, 10, TestResult)
            logger.info('正在回写测试结果test_result：{}'.format(TestResult))
            logger.info('*************结束回写数据***************')


if __name__ == '__main__':
    unittest.main()
