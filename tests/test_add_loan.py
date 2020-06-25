# -*- coding: utf-8 -*-
# @Time : 2020/6/18 23:33
# @Author : 深圳-烧烤-29期
# @File : test_add_loan.py
import unittest
import json, datetime
from ddt import ddt, data
from common import request_handler
from middleware import handler

# 初始化日志收集器
logger = handler.ConfHandler.logger

# 初始化handler
env_data = handler.ConfHandler()
# 调用配置文件解析模块
test_data = env_data.exl_handler.read_data(env_data.add_sheet)


@ddt
class TestAddLoan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = env_data.token
        cls.member_id = env_data.member_id

    def setUp(self):  # 前置条件
        self.exl = env_data.exl_handler
        self.db = env_data.db_class()

    def tearDown(self):  # 后置条件
        self.db.close()

    @data(*test_data)
    def test_add_loan(self, data_info):
        global testresult
        sum_num = 0
        # 登录获取的memberid替换掉excel的member_id
        if "#id#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#id#", str(self.member_id))

        # 动态获取title替换掉excel中项目名称
        title = "烧烤项目{}".format(datetime.datetime.now().strftime("%y%m%d%H%M"))
        if "#title#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#title#", title)

        # 登录获取的token替换掉excel的token
        if "#token#" in data_info["headers"]:
            data_info["headers"] = data_info["headers"].replace("#token#", self.token)

        # 只有yes_or_no的标识为YES的才查询member_id的项目个数
        if data_info['yes_or_no'] == "YES":
            logger.info("================正在查询member_id下原项目个数===============")
            sql_1 = "select count(*) record_num from loan where member_id = {};".format(self.member_id)
            original_num = self.db.query(sql_1)
            logger.info("账户id为{}的原项目个数为{}".format(self.member_id, original_num))
            # 预期充值成功后流水记录增加一条
            sum_num = original_num['record_num'] + 1 + sum_num

        logger.info('******************正在执行add_loan模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))

        # 拼接请求地址url
        url = "".join([env_data.host, data_info['url']])
        res = request_handler.visit(url,
                                    method=data_info['method'],
                                    json=json.loads(data_info['data']),
                                    headers=json.loads(data_info['headers']))
        try:
            # 预期结果与返回结果比对
            for k, v in eval(data_info['expected']).items():
                self.assertTrue(v == res[k])
            # 只有充值成功，code为0的才比对充值前后金额
            if res['code'] == 0:
                # 对新增项目成功的进行数据校验，判断数据是否已经落库
                logger.info("********************正在查询数据库********************")

                # 只有新增成功，code为0的才比对member_id下的项目个数
                logger.info("==============正在查询新增成功后member_id下的项目个数============")
                sql_2 = "select count(*)  record_num from loan where member_id = {};".format(
                    self.member_id)
                after_num = self.db.query(sql_2)
                logger.info("账户id为{}新增项目成功后的项目个数为{}".format(self.member_id, after_num))
                logger.info("======================正在项目个数比对=======================")
                self.assertTrue(after_num['record_num'] == sum_num)
            # 测试通过后，结果标记为pass
            testresult = 'PASS'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], testresult))
        except AssertionError as e:
            logger.error("执行接口测试出现错误，错误是{}".format(e))
            # 测试失败，结果标记为failed
            testresult = 'FAILED'
            logger.error("第{}条用例执行结果为{}".format(data_info['case_id'], testresult))
        finally:
            logger.info('*************开始回写数据***************')
            # 实际结果进行回写
            self.exl.write_excel(env_data.add_sheet, data_info['case_id'] + 1, 10, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            # 测试结果进行回写
            self.exl.write_excel(env_data.add_sheet, data_info['case_id'] + 1, 11, testresult)
            logger.info('正在回写测试结果test_result：{}'.format(testresult))
            logger.info('*************结束回写数据***************')


if __name__ == '__main__':
    unittest.main()
