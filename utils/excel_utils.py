# -*- coding: utf-8 -*-
"""
================================================================================
 Excel 测试数据读取工具
================================================================================
 职责：把 data/测试数据.xlsx 里的用例读成 [dict, dict, ...] 列表，
      供 test_runner.py 的 @parametrize 参数化使用。

 Excel 表结构约定（必须按这个格式维护用例表）：
     第 1 行：大标题（装饰用，程序不读）
     第 2 行：字段名 key 行（id、feature、story、title、method、path、headers、
              json、data、params、files、check、expected、sql_check、
              sql_excepted、jsonExData、sqlExData、is_true ...）
     第 3 行起：每行一条用例

 读取原理：
     keys  = 第 2 行所有单元格的值 → ['id', 'feature', ...]
     row   = 某一行的所有值       → [1, '登录', '登录成功', ...]
     zip(keys, row) → [('id',1), ('feature','登录'), ...] → dict() → 一条用例
================================================================================
"""

import openpyxl


def read_excel():
    # 打开工作簿（相对路径：必须在项目根目录 test_project/ 下执行才找得到）
    workbook = openpyxl.load_workbook("./data/测试数据.xlsx")
    # 选中数据所在的工作表（表名必须是 Sheet1）
    worksheet = workbook["Sheet1"]

    data = []  # 最终返回的用例列表

    # 拿 key 行（第 2 行）：
    # worksheet["2"] 表示整第 2 行，遍历其中每个单元格取 .value，
    # 生成形如 ['id', 'feature', 'story', ...] 的 key 列表。
    keys = [cell.value for cell in worksheet["2"]]

    # 从第 3 行开始逐行读取：
    # min_row=3        → 起始行号（跳过标题行和 key 行）
    # values_only=True → 每行只取单元格的值（不要单元格对象），得到一个元组
    for row in worksheet.iter_rows(min_row=3, values_only=True):
        # zip 把 key 列表和当前行的值一一配对，dict() 转成字典：
        # {'id': 1, 'feature': '登录', 'method': 'post', 'path': '/login', ...}
        dict_data = dict(zip(keys, row))
        # 用例开关：只有 is_true 列为 True 的行才会被收集执行。
        # 想临时跳过某条用例，把它的 is_true 改成 False 即可，不用删行。
        if dict_data["is_true"]:
            data.append(dict_data)

    workbook.close()  # 关闭工作簿，释放文件句柄
    return data
