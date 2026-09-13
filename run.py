# -*- coding: utf-8 -*-
"""测试入口：一键运行用例并生成 Allure 报告（python run.py）"""

import os

import pytest

if __name__ == "__main__":
    # 执行测试，原始结果输出到 ./report/json_report
    pytest.main(["-vs", "./testcases/test_runner.py", "--alluredir", "./report/json_report", "--clean-alluredir"])

    # 渲染 HTML 报告，浏览器打开 ./report/html_report/index.html 查看
    os.system("allure generate ./report/json_report -o ./report/html_report --clean")
