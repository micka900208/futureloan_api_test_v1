# -*- coding: utf-8 -*-
# @Time : 2020/6/13 22:23
# @Author : 深圳-烧烤-29期
# @File : test_invest.py

import unittest
import json, re
from ddt import ddt, data
from decimal import Decimal
from common import request_handler
from middleware import handler

# 初始化日志收集器
logger = handler.ConfHandler.logger

# 初始化handler
env_data = handler.ConfHandler()
# 调用配置文件解析模块
test_data = env_data.exl_handler.read_data(env_data.inv_sheet)


@ddt
class TestInvest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.token = env_data.invest_token
        cls.member_id = env_data.invest_member_id

    def setUp(self) -> None:
        self.exl = env_data.exl_handler
        self.db = env_data.db_class()
        self.loan_id = env_data.audit_loan()

    def tearDown(self) -> None:
        self.db.close()

    @data(*test_data)
    def test_invest(self, data_info):
        global testresult, loan_id, original_amt
        sum_amt, sum_invest, sum_log = 0, 0, 0
        logger.info('******************正在执行invest模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))
        if "#member_id#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#member_id#", str(self.member_id))
        if "#loanid#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#loanid#", str(self.loan_id))
        # 竞标中的项目
        if "#id#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#id#", str(self.loan_id))
            query = "select status from loan where id = {}".format(self.loan_id)
            loan_id = self.db.query(query)
            logger.info("项目id为{}审批前的状态为{}".format(self.loan_id, loan_id["status"]))

        # 非竞标中的项目 2-竞标中 3-还款中 4-还款完成 5-审核不通过
        if "#shz#" in data_info["data"]:  # 竞标中
            query_1 = "select id,status from loan where status = 1 limit 1"
            result = self.db.query(query_1)
            loan_id = result["id"]
            data_info["data"] = data_info["data"].replace("#shz#", str(loan_id))
        elif "#hkz#" in data_info["data"]:  # 还款中
            query_2 = "select id,status from loan where status = 3 limit 1"
            result = self.db.query(query_2)
            loan_id = result["id"]
            data_info["data"] = data_info["data"].replace("#hkz#", str(loan_id))
        elif "#hwc#" in data_info["data"]:  # 还款完成
            query_3 = "select id,status from loan where status = 4 limit 1"
            result = self.db.query(query_3)
            loan_id = result["id"]
            data_info["data"] = data_info["data"].replace("#hwc#", str(loan_id))
        elif "#btg#" in data_info["data"]:  # 审核不通过
            query_4 = "select id,status from loan where status = 5 limit 1"
            result = self.db.query(query_4)
            loan_id = result["id"]
            data_info["data"] = data_info["data"].replace("#btg#", str(loan_id))
        if "#otherid" in data_info["data"]:
            sql_2 = "select id,amount from loan where status = 2 and (amount between 200 and 20000) limit 1"
            other = self.db.query(sql_2)
            other_id = other["id"]
            data_info["data"] = data_info["data"].replace("#otherid#", str(other_id))
            if "#max_amt#" in data_info["data"]:
                data_info["data"] = data_info["data"].replace("#max_amt#", str(other["amount"] + 10000))
        elif "min_amt" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#max_amt#", str(original_amt + 10000))
        elif "#amount#" in data_info["data"]:
            sql_3 = "select amount from loan where id = {} limit 1".format(self.loan_id)
            amount = self.db.query(sql_3)
            eq_amount = amount["amount"]
            data_info["data"] = data_info["data"].replace("#amount#", str(eq_amount))

        # 只有yes_or_no的标识为YES的才查询原始金额
        if data_info['yes_or_no'] == "YES":
            logger.info("======================正在查询原始金额=======================")
            sql_1 = "select leave_amount from member where id = {};".format(self.member_id)
            original_data = self.db.query(sql_1)
            original_amt = original_data['leave_amount']

            # 判断账号是否余额充足，低于80000，则调充值接口，保证正常投资操作
            if original_amt < Decimal('80000'):
                original_amt = self.recharge()
                logger.info("账户id为{}的账户原始金额是{}".format(self.member_id, original_amt))
                sum_amt = original_amt - Decimal(json.loads(data_info['data'])['amount']) - sum_amt
            else:
                logger.info("账户id为{}的账户原始金额是{}".format(self.member_id, original_amt))
                sum_amt = original_amt - Decimal(json.loads(data_info['data'])['amount']) - sum_amt
                # 只有yes_or_no的标识为YES的才查询提现流水记录条数

        if "#other_id" in data_info["data"]:
            sql_0 = "select id from loan where status = 2 and (amount between 30000 and 80000) limit 1"
            other = self.db.query(sql_0)
            otherid = other["id"]
            data_info["data"] = data_info["data"].replace("#other_id#", str(otherid))
        elif "#max_id" in data_info["data"]:
            sql_2 = "select id,amount from loan where status = 2 and (amount between 200 and 20000) limit 1"
            other = self.db.query(sql_2)
            otherid = other["id"]
            data_info["data"] = data_info["data"].replace("#max_id#", str(otherid))
            # if "#max_amt#" in data_info["data"]:
            #     data_info["data"] = data_info["data"].replace("#max_amt#", str(other["amount"] + 10000))
        elif "#min_amt#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#min_amt#", str((original_amt + 10000)))
        elif "#amount#" in data_info["data"]:
            sql_3 = "select amount from loan where id = {} limit 1".format(self.loan_id)
            amount = self.db.query(sql_3)
            eq_amount = amount["amount"]
            data_info["data"] = data_info["data"].replace("#amount#", eq_amount)
        elif "#other_id" in data_info["data"]:
            sql_4 = "select id from loan where status = 2 and (amount between 500 and 20000) limit 1"
            other = self.db.query(sql_4)
            other_id = other["id"]
            data_info["data"] = data_info["data"].replace("#other_id#", str(other_id))

        logger.info("======================正在查询原始投资记录条数=======================")
        sql_5 = "select count(*) record_num from invest where member_id = {};".format(self.member_id)
        original_data = self.db.query(sql_5)
        original_num1 = original_data['record_num']
        logger.info("账户id为{}的原始投资记录条数为{}".format(self.member_id, original_num1))
        sum_invest = original_num1 + 1 + sum_invest

        logger.info("======================正在查询原始投资流水记录条数=======================")
        sql_6 = "select count(*) record_num from financelog where pay_member_id = {};".format(self.member_id)
        original_data = self.db.query(sql_6)
        original_num2 = original_data['record_num']
        logger.info("账户id为{}的原始投资流水条数为{}".format(self.member_id, original_num2))
        sum_log = original_num2 + 1 + sum_log

        # 正则替换headers的token
        while re.search("#.*?#", data_info["headers"]):
            data_info["headers"] = re.sub("#.*?#", self.token, data_info["headers"], 1)
        # 请求地址url拼接
        url = "".join([env_data.host, data_info['url']])
        res = request_handler.visit(url,
                                    method=data_info['method'],
                                    json=json.loads(data_info['data']),
                                    headers=json.loads(data_info['headers']))
        try:
            # 对返回结果进行断言
            self.assertTrue(eval(data_info['expected'])["code"] == res["code"])
            self.assertTrue(eval(data_info['expected'])["msg"] == res["msg"])
            # 只有充值成功，code为0的才比对充值前后金额
            if res['code'] == 0:
                logger.info("======================正在查询投资后金额=======================")
                sql_amt = "select leave_amount from member where id = {}".format(self.member_id)
                after_invest_data = self.db.query(sql_amt)
                after_invest_amt = after_invest_data['leave_amount']
                logger.info("账户id为{}的账户投资后的余额是{}".format(self.member_id, after_invest_amt))
                logger.info("账户id为{}的账户原始金额-投资金额后的余额是{}".format(self.member_id, sum_amt))
                logger.info("======================正在金额比对=======================")
                self.assertTrue(after_invest_amt == sum_amt)
                logger.info("======================金额比对通过=======================")
                logger.info("======================正在查询投资后流水记录=======================")
                sql_log = "select count(*)  record_num from financelog where pay_member_id = {};".format(self.member_id)
                after_data = self.db.query(sql_log)
                after_num = after_data['record_num']
                logger.info("账户id为{}的投资后流水条数为{}".format(self.member_id, after_num))
                logger.info("======================正在投资流水记录比对=======================")
                self.assertTrue(after_num == sum_log)
                logger.info("======================正在查询投资记录=======================")
                sql_invest = "select * from invest where member_id = {} and loan_id = {};".format(self.member_id,
                                                                                                  json.loads(data_info["data"])["loan_id"])
                after_invest = self.db.query(sql_invest)
                # after_num = after_data['record_num']
                self.assertTrue(after_invest)
                sql_status = "select status  from loan where id = {};".format(json.loads(data_info["data"])["loan_id"])
                after_invest = self.db.query(sql_status)
                if after_invest["status"] == 3:
                    sql_repay = "SELECT * from repayment where invest_id in (SELECT invest_id from invest where member_id = {} and loan_id={})".format(
                        self.member_id, json.loads(data_info["data"])["loan_id"])
                    self.assertTrue(sql_repay)
            testresult = 'PASS'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], testresult))
        except AssertionError as e:
            logger.error("执行接口测试出现错误，错误是{}".format(e))
            testresult = 'FAILED'
            logger.error("第{}条用例执行结果为{}".format(data_info['case_id'], testresult))
        finally:
            logger.info('*************开始回写数据***************')
            self.exl.write_excel(env_data.inv_sheet, data_info['case_id'] + 1, 10, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            self.exl.write_excel(env_data.inv_sheet, data_info['case_id'] + 1, 11, testresult)
            logger.info('正在回写测试结果test_result：{}'.format(testresult))
            logger.info('*************结束回写数据***************')

    # 充值操作，保证账号实现正常的提现流程
    def recharge(self):
        headers = {"X-Lemonban-Media-Type": "lemonban.v2", "Authorization": self.token}
        data = {"member_id": self.member_id, "amount": "20000"}
        url = "".join([env_data.host, "/member/recharge"])
        request_handler.visit(url,
                              method="POST",
                              json=data,
                              headers=headers)
        query_sql = "select leave_amount from member where id = {};".format(self.member_id)
        original_data = self.db.query(query_sql)
        original_amt = original_data['leave_amount']
        return original_amt


if __name__ == '__main__':
    unittest.main()

