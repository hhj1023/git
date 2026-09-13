# -*- coding: utf-8 -*-
"""
================================================================================
 测试入口（一键跑用例 + 生成 Allure 报告）
================================================================================
 作用：不用记 pytest 命令行参数，直接 python run.py 一键完成：
       ① 跑测试 → ② 生成 HTML 报告

 也可以不运行本文件，直接在命令行手动执行：
     pytest -vs ./testcases/test_runner.py --alluredir ./report/json_report --clean-alluredir
     allure generate ./report/json_report -o ./report/html_report --clean
================================================================================
"""

import os

import pytest

if __name__ == "__main__":
    # ---------------- ① 执行测试，收集原始结果 ----------------
    # pytest.main([...]) 等价于在命令行跑 pytest，参数含义：
    #   -vs                     ：-v 显示每条用例名，-s 显示 print 输出（看接口响应必加）
    #   ./testcases/test_runner.py ：只跑这个测试文件
    #   --alluredir ./report/json_report ：把测试结果输出成 allure 的原始数据（json）
    #   --clean-alluredir       ：先清空上一次的结果目录，避免新旧结果混在一起
    pytest.main(["-vs", "./testcases/test_runner.py", "--alluredir", "./report/json_report", "--clean-alluredir"])

    # ---------------- ② 把原始结果渲染成 HTML 报告 ----------------
    # os.system 调用系统的 allure 命令行工具（需要已安装 allure 并加入 PATH）：
    #   generate        ：把 json_report 里的原始数据渲染成网页
    #   -o ./report/html_report ：输出目录
    #   --clean         ：先清空输出目录
    # 生成后用浏览器打开 ./report/html_report/index.html 查看，
    # 或者用 allure open ./report/html_report 启动本地服务查看。
    os.system("allure generate ./report/json_report -o ./report/html_report --clean")
