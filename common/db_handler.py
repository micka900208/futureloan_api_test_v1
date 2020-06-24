# -*- coding: utf-8 -*-
# @Time : 2020/6/11 23:38
# @Author : 深圳-烧烤-29期
# @File : db_handler.py

import pymysql
from pymysql.cursors import DictCursor
from futureloan_api_test_v1.common import yaml_handler

conf_info=yaml_handler.read_yaml()
db_conf=conf_info['db']


class dbHandler:
    def __init__(self,
                 host='120.78.128.25',
                 port=3306,
                 user='future',
                 password='123456',
                 database='futureloan',
                 charset='utf8',
                 cursorclass=DictCursor
                 ):
        self.conn = pymysql.connect(host=host,
                                    port=port,
                                    user=user,
                                    password=password,
                                    database=database,
                                    charset=charset,
                                    cursorclass=cursorclass
                                    )
        self.cursor = self.conn.cursor()

    def query(self, sql, data_num=True):
        self.conn.commit()
        self.cursor.execute(sql)
        if data_num:
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()


