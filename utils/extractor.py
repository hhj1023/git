import logging
import allure
import jsonpath

from utils.send_request import send_jdbc_request


# JSON 提取：把响应值存入全局变量池，如 {"token": "$..token"}
def json_extractor(case,all,res):
    if case["jsonExData"]:
        with allure.step("4.JSON提取"):
            for key, value in eval(case["jsonExData"]).items():
                value = jsonpath.jsonpath(res.json(), value)[0]
                all[key] = value
            logging.info(f"4.JSON提取，根据{case['jsonExData']}提取数据，此时全局变量为{all}")

# 数据库提取：从数据库取值存入全局变量池，如新用户id
def jdbc_extractor(case,all):
    # with 要放在 if 里面：没有 sqlExData 的用例不应在报告里显示空的 JDBC 提取步骤
    if case["sqlExData"]:
        with allure.step("4.JDBC提取"):
            for key, value in eval(case["sqlExData"]).items():
                value = send_jdbc_request(value)
                all[key] = value

            logging.info(f"4.JDBC提取，根据{case['sqlExData']}提取数据，此时全局变量为{all}")