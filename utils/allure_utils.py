import allure

def allure_init(case):
    # Allure 动态打标（报告三级目录）
    allure.dynamic.feature(case["feature"])
    allure.dynamic.story(case["story"])
    allure.dynamic.title(f"{case['id']}--{case['title']}")
