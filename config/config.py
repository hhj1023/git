# -*- coding: utf-8 -*-
"""配置信息

敏感信息（数据库密码等）不写死在代码里，改为读取环境变量：
    Windows:  set DB_PASSWORD=123456
    macOS/Linux: export DB_PASSWORD=123456
    PyCharm:  Run/Debug Configurations -> Environment variables

所有变量都有默认值，不配置也能在本地默认环境直接跑；
只有密码没有默认值，未设置时为空字符串（避免把密码提交到公开仓库）。
"""

import os

# 被测服务地址
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8888/api/private/v1")

# excel测试用例文件配置
EXCEL_FILE = os.getenv("EXCEL_FILE", "./data/测试数据.xlsx")
SHEET_NAME = os.getenv("SHEET_NAME", "Sheet1")

# mysql配置信息
HOST = os.getenv("DB_HOST", "127.0.0.1")
PORT = int(os.getenv("DB_PORT", "3306"))
DATABASE = os.getenv("DB_NAME", "mydb")
USER = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "")
