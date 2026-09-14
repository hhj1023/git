"""
接口自动化测试执行器（项目核心文件）

流程：Excel 用例 → Jinja2 渲染 {{占位符}} → 发送请求 → HTTP/JDBC断言 → 提取变量供后续用例使用

登录用例在 Excel 中排在最前（先提取 token，后续用例才有值可渲染）

全流程幂等：用户/商品用例都是「创建 → 删除」闭环，重跑无需手动清库。
商品的删除接口是软删除（is_del=1，数据行仍留在表里），而 sp_goods.goods_name 有唯一索引，
因此商品名改用 {{now}} 动态生成（每次运行的时间戳都不同），避免重跑时同名冲突。
"""
import logging
import time

import pytest
from jinja2 import Template

from utils.allure_utils import allure_init
from utils.analyse_case import analyse_case
from utils.asserts import http_assert, jdbc_assert
from utils.excel_utils import read_excel
from utils.extractor import json_extractor, jdbc_extractor
from utils.send_request import send_http_request, send_jdbc_request

data = read_excel()

# 全局变量池：存放各用例提取的值（如 token、JAY_ID），供后续用例 {{变量}} 渲染
# now：本次运行的时间戳（毫秒级），用于生成「每次运行都不同」的数据（如商品名 测试商品{{now}}）。
#      目的是让用例可重复执行 —— 商品是软删除且 goods_name 有唯一索引，用固定名字第二次会冲突
all = {"now": int(time.time() * 1000)}


class TestRunner:
    """所有 Excel 用例汇聚到一个方法，靠参数化逐条执行"""

    @pytest.mark.parametrize("case", data)
    def test_login(self, case):

        # 渲染模板：把{{xxx}}占位符替换成全局变量池的值，eval还原为dict
        case = eval(Template(str(case)).render(all))

        #显示日志信息
        # 注意：f-string 里嵌套的引号要用单引号，避免外层双引号冲突（Python 3.12 以下会直接语法报错）
        logging.info(f"用例ID：{case['id']},模块：{case['feature']},场景：{case['story']},标题：{case['title']}")

        #初始化报告
        allure_init(case)

        #解析请求数据
        request_data=analyse_case(case)

        # 发送请求，得到响应结果
        res = send_http_request(**request_data)

        #HTTP响应断言
        http_assert(case,res)

        #数据库断言
        jdbc_assert(case)

        #JSON提取
        json_extractor(case,all,res)

        #JDBC提取
        jdbc_extractor(case,all)





