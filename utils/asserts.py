import allure
import jsonpath
import logging

from utils.send_request import send_jdbc_request

@allure.step("3.HTTP响应断言")
def http_assert(case,res):
        # HTTP断言：jsonpath精确比较
    if case["check"]:
        actual = jsonpath.jsonpath(res.json(), case["check"])[0]
        logging.info(f"3.HTTP响应断言,实际结果({actual})==预期结果({case['expected']})")

        assert actual == case["expected"]
    else:
        logging.info(f"3.HTTP响应断言,预期结果({case['expected']}) in 实际结果({res.text})")
        assert case["expected"] in res.text

# @allure.step("3.JDBC响应断言") 
def jdbc_assert(case):
    # 数据库断言：校验接口是否真正写库成功
    if case["sql_check"] and case["sql_excepted"]:
        with allure.step("3.JDBC响应断言"):
            result = send_jdbc_request(case["sql_check"], index=0)  # 返回第一行，是元组，如 ('admin',)
            logging.info(f"3.JDBC响应断言,实际结果({result[0]})==预期结果({case['sql_excepted']})")
            # result[0] 取该行第一列的值（字符串）
            assert result[0] == case["sql_excepted"]
