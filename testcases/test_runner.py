# -*- coding: utf-8 -*-
"""
接口自动化测试执行器（项目核心文件）

流程：Excel 用例 → Jinja2 渲染 {{占位符}} → 发送请求 → HTTP/DB 断言 → 提取变量供后续用例使用
注意：
  - 登录用例必须在 Excel 中排在最前（先提取 token，后续用例才有值可渲染）
  - "创建用户 hhj" 用例非幂等，重跑前需清理数据：DELETE FROM mydb.sp_manager WHERE mg_name='hhj';
"""

import allure
import jsonpath
import pymysql
import pytest
import requests
from jinja2 import Template

from utils.excel_utils import read_excel

# 被测服务地址（结尾不带斜杠，避免与 path 的前导斜杠拼出 // 导致鉴权失败）
BASE_URL = "http://127.0.0.1:8888/api/private/v1"

data = read_excel()

# 全局变量池：存放各用例提取的值（如 token、JAY_ID），供后续用例 {{变量}} 渲染
all = {}


class TestRunner:
    """所有 Excel 用例汇聚到一个方法，靠参数化逐条执行"""

    @pytest.mark.parametrize("case", data)
    def test_login(self, case):

        # ① 渲染模板：把 {{xxx}} 占位符替换成全局变量池的值，eval 还原为 dict
        case = eval(Template(str(case)).render(all))

        # ② Allure 动态打标（报告三级目录）
        allure.dynamic.feature(case["feature"])
        allure.dynamic.story(case["story"])
        allure.dynamic.title(f"{case['id']}--{case['title']}")

        # ③ 解析请求参数（Excel 单元格为字符串时 eval 还原为 dict）
        method = case["method"]
        # 去掉 path 前导斜杠后统一拼接，避免双斜杠
        url = f"{BASE_URL}/{str(case['path']).lstrip('/')}"

        headers = eval(case["headers"]) if isinstance(case["headers"], str) else None   # 请求头
        json_body = eval(case["json"]) if isinstance(case["json"], str) else None       # JSON 请求体
        form_data = eval(case["data"]) if isinstance(case["data"], str) else None       # 表单请求体
        params = eval(case["params"]) if isinstance(case["params"], str) else None      # URL 查询参数
        files = eval(case["files"]) if isinstance(case["files"], str) else None         # 上传文件

        # ④ 组装并发送请求（统一打包，无需区分请求类型；None 参数会被 requests 忽略）
        request_data = {
            "method": method,
            "url": url,
            "headers": headers,
            "json": json_body,
            "data": form_data,
            "params": params,
            "files": files,
        }
        res = requests.request(**request_data)
        print(res.json())

        # ⑤ HTTP 断言：填了 jsonpath 则精确比较，否则模糊匹配响应文本
        if case["check"]:
            actual = jsonpath.jsonpath(res.json(), case["check"])[0]
            assert actual == case["expected"], f"预期[{case['expected']}]，实际[{actual}]，响应：{res.json()}"
        else:
            assert case["expected"] in res.text, f"预期[{case['expected']}]，实际响应：{res.text}"

        # ⑥ DB 断言（可选）：校验接口是否真正写库成功
        if case["sql_check"] and case["sql_excepted"]:
            conn = pymysql.Connect(
                host="127.0.0.1",
                port=3306,
                database="mydb",
                user="root",
                password="123456",
                charset="utf8",
            )
            cur = conn.cursor()
            cur.execute(case["sql_check"])
            db_result = cur.fetchall()
            cur.close()
            conn.close()
            assert db_result[0][0] == case["sql_excepted"]

        # ⑦ JSON 提取：把响应值存入全局变量池，如 {"token": "$..token"}
        if case["jsonExData"]:
            for key, value in eval(case["jsonExData"]).items():
                all[key] = jsonpath.jsonpath(res.json(), value)[0]

        # ⑧ DB 提取（可选）：从数据库取值存入全局变量池，如新用户 id
        if case["sqlExData"]:
            for key, value in eval(case["sqlExData"]).items():
                conn = pymysql.Connect(
                    host="127.0.0.1",
                    port=3306,
                    database="mydb",
                    user="root",
                    password="123456",
                    charset="utf8",
                )
                cur = conn.cursor()
                cur.execute(value)
                db_result = cur.fetchall()
                cur.close()
                conn.close()
                all[key] = db_result[0]
