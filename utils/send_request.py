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
        # 密码改为环境变量后不再有默认值，未配置时给出明确提示：
        # 否则会因用例1查库失败导致 token 提取不到，后续用例连锁失败，很难定位原因
        if not PASSWORD:
            raise RuntimeError(
                "未设置数据库密码，请先配置环境变量 DB_PASSWORD 再运行"
                "（见 .env.example；PyCharm 在 Run/Debug Configurations 的 Environment variables 中配置）"
            )
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
