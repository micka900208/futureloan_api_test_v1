# -*- coding: utf-8 -*-
# @Time : 2020/5/26 22:48
# @Author : 深圳-烧烤-29期
# @File : test_0526_shaokao.py

import unittest, random,json
from ddt import ddt, data
from futureloan_api_test_v1.common import request_handler
from futureloan_api_test_v1.middleware import handler

# 初始化日志收集器
logger = handler.ConfHandler.logger

# 初始化handler
env_data = handler.ConfHandler()
# 调用配置文件解析模块
test_data = env_data.exl_handler.read_data(env_data.regist_sheet)


@ddt
class TestRegist(unittest.TestCase):
    def setUp(self):  # 前置条件
        self.exl = env_data.exl_handler
        self.db = env_data.db_class()

    def tearDown(self):  # 后置条件
        self.db.close()

    @data(*test_data)
    def test_regist(self, data_info):
        global test_result
        # 替换动态手机号，用于注册成功用例
        phone = self.phone_no()
        if '#phone#' in data_info['data']:
            data_info['data'] = data_info['data'].replace('#phone#', phone)
        logger.info('******************正在执行register模块用例******************')
        logger.info('正在执行第{}条用例:{}'.format(data_info['case_id'], data_info['title']))
        logger.info('请求的数据是{}'.format(data_info))
        # 请求地址拼接
        url = "".join([env_data.host, data_info['url']])

        res = request_handler.visit(url,
                                    method=data_info['method'],
                                    json=eval(data_info['data']),
                                    headers=json.loads(data_info['headers']))
        try:
            # 预期结果与返回结果比对
            for k, v in eval(data_info['expected']).items():
                self.assertTrue(v == res[k])
            # 对注册成功的进行数据校验，判断数据是否已经落库
            logger.info("********************正在查询数据库********************")
            sql = 'select * from member where mobile_phone={}'.format(phone)
            query_res = self.db.query(sql)
            if res['code'] == 0:
                self.assertTrue(query_res)
            # 若断言成功，则测试结果为pass
            test_result = 'PASS'
            logger.info("第{}条用例执行结果为{}".format(data_info['case_id'], test_result))
        except AssertionError as e:
            logger.error("执行接口测试出现错误，错误是{}".format(e))
            # 若断言成功，则测试结果为failed
            test_result = 'FAILED'
            logger.error("第{}条用例执行结果为{}".format(data_info['case_id'], test_result))
        finally:
            logger.info('*************开始回写数据***************')
            # 实际结果进行回写
            self.exl.write_excel(env_data.regist_sheet, data_info['case_id'] + 1, 9, str(res))
            logger.info('正在回写实际结果actual：{}'.format(str(res)))
            # 测试结果进行回写
            self.exl.write_excel(env_data.regist_sheet, data_info['case_id'] + 1, 10, test_result)
            logger.info('正在回写测试结果test_result：{}'.format(test_result))
            logger.info('*************结束回写数据***************')

    # 动态手机号生成
    def phone_no(self):
        while True:
            mobile_segment = random.choice([3, 5, 8])
            nine_code = random.randint(000000000, 999999999)
            mobile_phone = '1' + str(mobile_segment) + str(nine_code)
            sql = "select * from member where mobile_phone = {}".format(mobile_phone)
            query_data = self.db.query(sql)
            if not query_data:
                return mobile_phone
            self.db.close()


if __name__ == '__main__':
    unittest.main()
