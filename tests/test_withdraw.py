# -*- coding: utf-8 -*-
# @Time : 2020/6/13 15:08
# @Author : 深圳-烧烤-29期
# @File : test_withdraw.py

import unittest, json
from decimal import Decimal
from ddt import ddt, data
from common import request_handler
from middleware import handler

# 初始化日志收集器
logger = handler.ConfHandler.logger

# 初始化handler
env_data = handler.ConfHandler()

# 调用配置文件解析模块
test_data = env_data.exl_handler.read_data(env_data.withdraw_sheet)


@ddt
class TestWithdraw(unittest.TestCase):
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
    def test_withdraw(self, data_info):
        global testresult
        sum_amt, sum_num = 0, 0

        # 登录获取的memberid替换掉excel的member_id
        if "#id#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#id#", str(self.member_id))

        # 登录获取的token替换掉excel的token
        if "#token#" in data_info["headers"]:
            data_info["headers"] = data_info["headers"].replace("#token#", self.token)

        logger.info('******************正在执行withdraw模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))

        # 提现金额大于账户余额
        if '#max_id#' in data_info['data']:
            sql = "select id,leave_amount from member where leave_amount between 1000 and 50000 limit 1"
            m_data = self.db.query(sql)
            draw_amt = m_data['leave_amount'] + 1000
            data_info['data'] = data_info['data'].replace('#max_id#', str(m_data['id']))
            data_info['data'] = data_info['data'].replace('#amt#', str(draw_amt))

        # 只有yes_or_no的标识为YES的才查询原始金额
        if data_info['yes_or_no'] == "YES":
            logger.info("======================正在查询原始金额=======================")
            sql_1 = "select leave_amount from member where id = {};".format(self.member_id)
            original_data = self.db.query(sql_1)
            original_amt = original_data['leave_amount']

            # 判断账号是否余额充足，低于500000，则调充值接口，保证正常提现操作
            if original_amt < Decimal('500000'):
                before_amt = self.recharge()
                logger.info("账户id为{}的账户原始金额是{}".format(self.member_id, before_amt))
                sum_amt = before_amt - Decimal(json.loads(data_info['data'])['amount']) - sum_amt
            else:
                logger.info("账户id为{}的账户原始金额是{}".format(self.member_id, original_amt))
                sum_amt = original_amt - Decimal(json.loads(data_info['data'])['amount']) - sum_amt
            # 只有yes_or_no的标识为YES的才查询提现流水记录条数
            logger.info("======================正在查询原始提现流水记录条数=======================")
            sql_2 = "select count(*) record_num from financelog where pay_member_id = {};".format(self.member_id)
            original_data = self.db.query(sql_2)
            original_num = original_data['record_num']
            logger.info("账户id为{}的原始提现流水条数为{}".format(self.member_id, original_num))
            sum_num = original_num + 1 + sum_num
        url = "".join([env_data.host, data_info['url']])
        res = request_handler.visit(url,
                                    method=data_info['method'],
                                    json=json.loads(data_info['data']),
                                    headers=json.loads(data_info['headers']))
        try:
            for k, v in eval(data_info['expected']).items():
                self.assertTrue(v == res[k])
            # 只有充值成功，code为0的才比对充值前后金额
            if res['code'] == 0:
                logger.info("======================正在查询提现后金额=======================")
                sql_3 = "select leave_amount from member where id = {}".format(self.member_id)
                after_withdraw_data = self.db.query(sql_3)
                after_withdraw_amt = after_withdraw_data['leave_amount']
                logger.info("账户id为{}的账户提现后的金额是{}".format(self.member_id, after_withdraw_amt))
                logger.info("账户id为{}的账户原始金额-提现金额后的余额是{}".format(self.member_id, sum_amt))
                logger.info("======================正在金额比对=======================")
                self.assertTrue(after_withdraw_amt == sum_amt)
                logger.info("======================金额比对通过=======================")
                logger.info("======================正在查询提现后流水记录=======================")
                sql_4 = "select count(*)  record_num from financelog where pay_member_id = {};".format(self.member_id)
                after_data = self.db.query(sql_4)
                after_num = after_data['record_num']
                logger.info("账户id为{}的提现后流水条数为{}".format(self.member_id, after_num))
                logger.info("======================正在提现流水比对=======================")
                self.assertTrue(after_num == sum_num)
            testresult = 'PASS'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], testresult))
        except AssertionError as e:
            logger.error("执行接口测试出现错误，错误是{}".format(e))
            testresult = 'FAILED'
            logger.error("第{}条用例执行结果为{}".format(data_info['case_id'], testresult))
        finally:
            logger.info('*************开始回写数据***************')
            self.exl.write_excel(env_data.withdraw_sheet, data_info['case_id'] + 1, 10, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            self.exl.write_excel(env_data.withdraw_sheet, data_info['case_id'] + 1, 11, testresult)
            logger.info('正在回写测试结果test_result：{}'.format(testresult))
            logger.info('*************结束回写数据***************')

    # 充值操作，保证账号实现正常的提现流程
    def recharge(self):
        headers = {"X-Lemonban-Media-Type": "lemonban.v2", "Authorization": self.token}
        data = {"member_id": self.member_id, "amount": "500000"}
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
