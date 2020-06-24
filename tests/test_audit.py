# -*- coding: utf-8 -*-
# @Time : 2020/6/19 1:15
# @Author : 深圳-烧烤-29期
# @File : test_audit.py
import unittest
import json
from ddt import ddt, data
from futureloan_api_test_v1.common import request_handler
from futureloan_api_test_v1.middleware import handler

# 初始化日志收集器
logger = handler.ConfHandler.logger

# 初始化handler
env_data = handler.ConfHandler()
# 调用配置文件解析模块
test_data = env_data.exl_handler.read_data(env_data.audit_sheet)


@ddt
class TestAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.token = env_data.token
        cls.member_id = env_data.member_id
        cls.admin_token = env_data.admin_token

    def setUp(self) -> None:
        self.exl = env_data.exl_handler
        self.db = env_data.db_class()
        self.loan_id = env_data.loan_id

    def tearDown(self) -> None:
        self.db.close()

    @data(*test_data)
    def test_audit(self, data_info):
        global testresult, loan_id
        logger.info('******************正在执行audit模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))
        # 审核中的项目
        if "#id#" in data_info["data"]:
            data_info["data"] = data_info["data"].replace("#id#", str(self.loan_id))
            query = "select status from loan where id = {}".format(self.loan_id)
            loan_id = self.db.query(query)
            logger.info("项目id为{}审批前的状态为{}".format(self.loan_id, loan_id["status"]))

        # 非审核中的项目 2-竞标中 3-还款中 4-还款完成 5-审核不通过
        if "#jbz#" in data_info["data"]:# 竞标中
            query_1 = "select id,status from loan where status = 2 limit 1"
            result = self.db.query(query_1)
            loan_id = result["id"]
            data_info["data"] = data_info["data"].replace("#jbz#", str(loan_id))
            logger.info("项目id为{}审批前的状态为{}".format(loan_id, result["status"]))
        elif "#hkz#" in data_info["data"]:# 还款中
            query_2 = "select id,status from loan where status = 3 limit 1"
            result = self.db.query(query_2)
            loan_id=result["id"]
            data_info["data"] = data_info["data"].replace("#hkz#", str(loan_id))
            logger.info("项目id为{}审批前的状态为{}".format(loan_id, result["status"]))
        elif "#hwc#" in data_info["data"]:# 还款完成
            query_3 = "select id,status from loan where status = 4 limit 1"
            result = self.db.query(query_3)
            loan_id = result["id"]
            data_info["data"] = data_info["data"].replace("#hwc#", str(loan_id))
            logger.info("项目id为{}审批前的状态为{}".format(loan_id, result["status"]))
        elif "#btg#" in data_info["data"]:# 审核不通过
            query_4 = "select id,status from loan where status = 5 limit 1"
            result = self.db.query(query_4)
            loan_id = result["id"]
            data_info["data"] = data_info["data"].replace("#btg#", str(loan_id))
            logger.info("项目id为{}审批前的状态为{}".format(loan_id, result["status"]))

        # 替换headers里面的token为admin token
        if "#adtoken#" in data_info["headers"]:
            data_info["headers"] = data_info["headers"].replace("#adtoken#", self.admin_token)
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
            # 校验项目状态
            if data_info['yes_or_no'] == "YES":
                logger.info("======================正在查询项目状态=======================")
                if res["code"] in (0,1):
                    sql = "select status from loan where id = {}".format(self.loan_id)
                    after_status = self.db.query(sql)
                    logger.info("项目id为{}审批后的状态为{}".format(self.loan_id, after_status["status"]))
                    logger.info("======================正在状态比对=======================")
                    self.assertTrue(after_status["status"] == eval(data_info['expected'])["status"])
                elif res["code"] == 2:
                    sql = "select status from loan where id = {}".format(loan_id)
                    after_status = self.db.query(sql)
                    logger.info("项目id为{}审批后的状态为{}".format(loan_id, after_status["status"]))
                    logger.info("======================正在状态比对=======================")
                    self.assertTrue(after_status["status"] == json.loads(data_info['expected'])["status"])
            testresult = 'PASS'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], testresult))
        except AssertionError as e:
            logger.error("执行接口测试出现错误，错误是{}".format(e))
            testresult = 'FAILED'
            logger.error("第{}条用例执行结果为{}".format(data_info['case_id'], testresult))
        finally:
            logger.info('*************开始回写数据***************')
            self.exl.write_excel(env_data.audit_sheet, data_info['case_id'] + 1, 10, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            self.exl.write_excel(env_data.audit_sheet, data_info['case_id'] + 1, 11, testresult)
            logger.info('正在回写测试结果test_result：{}'.format(testresult))
            logger.info('*************结束回写数据***************')


if __name__ == '__main__':
    unittest.main()

