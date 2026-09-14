"""
读取 data/测试数据.xlsx，返回用例字典列表供参数化使用
Excel：第 1 行大标题（不读）；第 2 行字段名；第 3 行起每行一条用例
"""

import openpyxl

from config.config import EXCEL_FILE, SHEET_NAME


def read_excel(file_path=EXCEL_FILE,sheet_name=SHEET_NAME):
    # 相对路径：在项目根目录下执行
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook[sheet_name]

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
