# -*- coding: utf-8 -*-
# @Time : 2020/6/13 11:59
# @Author : 深圳-烧烤-29期
# @File : handler.py
import datetime
import os
from jsonpath import jsonpath
from pymysql.cursors import DictCursor

from common import yaml_handler, logging_handler, excel_read
from common.db_handler import dbHandler
from common import request_handler
from config import path_config


class dbHandlerMid(dbHandler):

    def __init__(self):
        db_conf = ConfHandler.conf_info['db']
        super().__init__(host=db_conf['host'],
                         port=db_conf['port'],
                         user=db_conf['user'],
                         password=db_conf['password'],
                         database=db_conf['database'],
                         charset='utf8',
                         cursorclass=DictCursor
                         )


class ConfHandler:
    # 获取配置文件内容
    conf_info = yaml_handler.read_yaml()

    # excel配置信息
    __excel_data = conf_info['excel']
    regist_sheet = __excel_data['sheet_name_reg']
    login_sheet = __excel_data['sheet_name_lgn']
    recharge_sheet = __excel_data['sheet_name_chrg']
    withdraw_sheet = __excel_data['sheet_name_wthdr']
    update_sheet = __excel_data['sheet_name_name']
    info_sheet = __excel_data['sheet_name_info']
    add_sheet = __excel_data['sheet_name_add']
    audit_sheet = __excel_data['sheet_name_audit']
    inv_sheet = __excel_data['sheet_name_inv']
    loans_sheet = __excel_data['sheet_name_loans']

    # excel路径
    excel_file = path_config.exl_path
    # 初始化excel数据读取
    exl_handler = excel_read.ExcelHandler(excel_file)

    # log配置信息
    __log_conf = conf_info['log']
    # 配置日志存放路径
    __lg_mk = datetime.datetime.now().strftime("%y%m%d")
    __lg_fl = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")

    __lg_path = os.path.join(path_config.logs_path, __lg_mk)
    # 判断文件夹是否存在
    if not os.path.exists(__lg_path):
        os.mkdir(__lg_path)
    __logs_file = os.path.join(__lg_path, "futureloan-{}.log".format(__lg_fl))
    # 初始化日志收集器
    logger = logging_handler.get_logger(name=__log_conf['name'],
                                        logger_level=__log_conf['logger_level'],
                                        stream_level=__log_conf['stream_level'],
                                        file_level=__log_conf['file_level'],
                                        file=__logs_file
                                        )
    # 测试报告配置信息
    rpt_conf = conf_info['report']

    __rp_mk = datetime.datetime.now().strftime("%y%m%d")
    __rp_fl = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")

    __rp_path = os.path.join(path_config.repors_path, __rp_mk)

    # 判断文件夹是否存在
    if not os.path.exists(__rp_path):
        os.mkdir(__rp_path)
    # 测试报告存放路径
    rpt_file = os.path.join(__rp_path, "report-{}.html".format(__rp_fl))

    # host地址
    host = conf_info['host']

    # 封装数据库类名
    db_class = dbHandlerMid

    @property
    def token(self):
        return self.login(self.conf_info["user"])['token']

    @property
    def member_id(self):
        return self.login(self.conf_info["user"])['member_id']

    @property
    def admin_token(self):
        return self.login(self.conf_info["admin_user"])["token"]

    @property
    def invest_token(self):
        return self.login(self.conf_info["invest_user"])["token"]

    @property
    def invest_member_id(self):
        return self.login(self.conf_info["invest_user"])["member_id"]

    @property
    def loan_id(self):
        return self.add_loan()

    def login(self, user):
        res = request_handler.visit(url="".join([ConfHandler.host, "/member/login"]),
                                    method="POST",
                                    json=user,
                                    headers={"X-Lemonban-Media-Type": "lemonban.v2"}
                                    )
        # 取token的前缀
        token_type = jsonpath(res, "$..token_type")[0]
        # 取token后半部分
        token_str = jsonpath(res, "$..token")[0]
        # 拼接token
        token = " ".join([token_type, token_str])
        # 获取登录用户的id
        id = jsonpath(res, "$..id")[0]

        return {"token": token, "member_id": id}

    # 新增项目
    def add_loan(self):
        data = {"member_id": self.invest_member_id,
                "title": "烧烤投资{}".format(datetime.datetime.now().strftime("%y%m%d%H%M%S")),
                "amount": 80000.00,
                "loan_rate": 12.0,
                "loan_term": 12,
                "loan_date_type": 1,
                "bidding_days": 10
                }
        res = request_handler.visit(url="".join([self.host, "/loan/add"]),
                                    method="POST",
                                    json=data,
                                    headers={"X-Lemonban-Media-Type": "lemonban.v2", "Authorization": self.invest_token}
                                    )
        # 返回新增项目的loan_id
        return jsonpath(res, "$..id")[0]

    # 审核项目
    def audit_loan(self):
        data = {"loan_id": self.loan_id, "approved_or_not": "true"}
        res = request_handler.visit(url="".join([self.host, "/loan/audit"]),
                                    method="PATCH",
                                    json=data,
                                    headers={"X-Lemonban-Media-Type": "lemonban.v2", "Authorization": self.admin_token}
                                    )
        return jsonpath(data,"$.loan_id")[0]

    def replace_data(self,data):
        import re
        patten = r"#(.*?)#"
        while re.search(patten,data):
            key = re.search(patten,data).group(1)
            value = getattr(self,key,"")
            data = re.sub(patten,str(value),data,1)
        return data
    

if __name__ == '__main__':
    lg = ConfHandler()
    # print(lg.token)
    # print(lg.admin_token)
    # print(lg.add_loan())
    print(lg.audit_loan())
