# -*- coding: utf-8 -*-
# @Time : 2020/6/12 22:54
# @Author : 深圳-烧烤-29期
# @File : test_recharge.py
import unittest, json
from decimal import Decimal
from ddt import ddt, data
from futureloan_api_test_v1.common import request_handler
from futureloan_api_test_v1.middleware import handler

# 实例一个日志收集器
logger = handler.ConfHandler.logger

# 初始化handler
env_data = handler.ConfHandler()

# 调用配置文件解析模块
test_data = env_data.exl_handler.read_data(env_data.recharge_sheet)


@ddt
class TestRecharge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = env_data.token
        cls.member_id = env_data.member_id

    def setUp(self):
        self.exl = env_data.exl_handler
        self.db = env_data.db_class()

    def tearDown(self):
        self.db.close()

    @data(*test_data)
    def test_recharge(self, data_info):
        global testresult
        sum_amt, sum_num = 0, 0

        # 登录获取的memberid替换掉excel的member_id
        if "#id#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#id#", str(self.member_id))

        # 登录获取的token替换掉excel的token
        if "#token#" in data_info["headers"]:
            data_info["headers"] = data_info["headers"].replace("#token#", self.token)

        logger.info('******************正在执行recharge模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))

        # 只有yes_or_no的标识为YES的才查询原始金额
        if data_info['yes_or_no'] == "YES":
            logger.info("======================正在查询原始金额=======================")
            sql = "select leave_amount from member where id = {};".format(self.member_id)
            before_amt = self.db.query(sql)
            logger.info("账户id为{}的账户原始金额是{}".format(self.member_id, before_amt))
            # 若充值成功，预期余额
            sum_amt = before_amt['leave_amount'] + Decimal(json.loads(data_info['data'])['amount']) + sum_amt

            # 只有yes_or_no的标识为YES的才查询充值流水记录条数
            logger.info("======================正在查询原始充值流水记录条数=======================")
            sql_1 = "select count(*) record_num from financelog where income_member_id = {};".format(self.member_id)
            original_num = self.db.query(sql_1)
            logger.info("账户id为{}的原始充值流水条数为{}".format(self.member_id, original_num))
            # 预期充值成功后流水记录增加一条
            sum_num = original_num['record_num'] + 1 + sum_num

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
                logger.info("======================正在查询充值后金额=======================")
                sql_2 = "select leave_amount from member where id = {}".format(self.member_id)
                after_amt = self.db.query(sql_2)
                logger.info(
                    "账户id为{}的账户充值后的金额是{}".format(self.member_id, after_amt))
                logger.info("账户id为{}的账户原始金额与充值金额求和的金额是{}".format(self.member_id, sum_amt))
                logger.info("======================正在金额比对=======================")
                self.assertTrue(after_amt['leave_amount'] == sum_amt)
                # 只有充值成功，code为0的才比对充值流水记录
                logger.info("======================正在查询充值后流水记录=======================")
                sql_no = "select count(*)  record_num from financelog where income_member_id = {};".format(
                    self.member_id)
                after_num = self.db.query(sql_no)
                logger.info("账户id为{}的充值后流水条数为{}".format(self.member_id, after_num))
                logger.info("======================正在充值流水比对=======================")
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
            self.exl.write_excel(env_data.recharge_sheet, data_info['case_id'] + 1, 10, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            # 测试结果进行回写
            self.exl.write_excel(env_data.recharge_sheet, data_info['case_id'] + 1, 11, testresult)
            logger.info('正在回写测试结果test_result：{}'.format(testresult))
            logger.info('*************结束回写数据***************')


if __name__ == '__main__':
    unittest.main()
