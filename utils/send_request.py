import logging
import allure
import pymysql
import requests

from config.config import *


@allure.step("2.发送HTTP请求")
def send_http_request(**requests_data):
    res=requests.request(**requests_data)
    logging.info(f"2.发送HTTP请求,响应文本：{res.text}")
    return res

def send_jdbc_request(sql,index=0):
        conn = pymysql.Connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
        )
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result[index]
