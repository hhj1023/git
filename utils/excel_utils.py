# -*- coding: utf-8 -*-
"""读取 data/测试数据.xlsx，返回用例字典列表供参数化使用

Excel 约定：第 1 行大标题（不读）；第 2 行字段名；第 3 行起每行一条用例
"""

import openpyxl


def read_excel():
    # 相对路径：需在项目根目录下执行
    workbook = openpyxl.load_workbook("./data/测试数据.xlsx")
    worksheet = workbook["Sheet1"]

    data = []
    # 第 2 行为 key 行
    keys = [cell.value for cell in worksheet["2"]]

    for row in worksheet.iter_rows(min_row=3, values_only=True):
        dict_data = dict(zip(keys, row))
        # 用例开关：is_true 为 False 的行跳过（临时禁用用例改此列即可）
        if dict_data["is_true"]:
            data.append(dict_data)

    workbook.close()
    return data
