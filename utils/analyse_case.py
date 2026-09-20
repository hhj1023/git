import logging

from config.config import BASE_URL
import allure

@allure.step("1、解析请求数据")#报告展示测试步骤
def analyse_case(case):

    method = case["method"]
    # lstrip('/') 无论 Excel 里 path 带不带前导斜杠都只拼一个 /
    url = BASE_URL + "/" + str(case['path']).lstrip('/')

    # 解析请求参数（Excel 单元格为字符串时 eval 还原为 dict）
    headers = eval(case["headers"]) if isinstance(case["headers"], str) else None  # 请求头
    json_body = eval(case["json"]) if isinstance(case["json"], str) else None  # JSON 请求体
    form_data = eval(case["data"]) if isinstance(case["data"], str) else None  # 表单请求体
    params = eval(case["params"]) if isinstance(case["params"], str) else None  # URL 查询参数
    files = eval(case["files"]) if isinstance(case["files"], str) else None  # 上传文件

    # 组装并发送请求（统一打包，无需区分请求类型；None 参数会被 requests 忽略）
    request_data = {
        "method": method,
        "url": url,
        "headers": headers,
        "json": json_body,
        "data": form_data,
        "params": params,
        "files": files,
    }

    logging.info(f"1.解析请求数据：{request_data}")
    allure.attach(f"{request_data}",name="解析数据结果")#增加附件信息
    #返回数据结果
    return request_data
