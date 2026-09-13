# -*- coding: utf-8 -*-
"""
================================================================================
 接口自动化测试执行器（本项目最核心的文件）
================================================================================

【整体执行流程】（一条用例从 Excel 到断言的完整链路）：

    测试数据.xlsx ──read_excel()──> [dict, dict, ...] 用例列表
                                          │
                     pytest 参数化 @parametrize（一条用例跑一次 test_login）
                                          │
                                          ▼
              ① Jinja2 渲染：把 {{token}}、{{JAY_ID}} 替换成全局变量池 all 里的真实值
                  │
              ② 组装 requests 请求（method/url/headers/json/data/params/files）
                  │
              ③ 发请求，拿到响应 res
                  │
              ④ HTTP 断言：用 jsonpath 从响应里取实际值，和 Excel 的"预期结果"比对
                  │
              ⑤ DB 断言（可选）：pymysql 查库，比对 Excel 的 sql 预期值
                  │
              ⑥ 变量提取（可选）：把响应里的 token / 用户id 存进全局变量池 all，
                  供后面的用例在 ① 步渲染使用 —— 这就是"用例间传参"的实现方式

【Excel 表格约定】（详见 utils/excel_utils.py）：
    第 1 行：标题（不使用）
    第 2 行：字段名 key 行（id/feature/story/title/method/path/headers/...）
    第 3 行起：每行一条用例；is_true 列为 True 才会被收集执行

【重跑须知】"创建用户 hhj"用例不是幂等的：
    跑过一次后数据库里就存在 hhj，再跑会返回"用户名已存在"导致用例失败。
    重跑前先清理残留数据（注意：管理员接口对应的表是 sp_manager）：
        DELETE FROM mydb.sp_manager WHERE mg_name='hhj';
================================================================================
"""

import allure
import jsonpath
import pymysql
import pytest
import requests
from jinja2 import Template

from utils.excel_utils import read_excel

# ------------------------------------------------------------------------------
# 被测服务基础地址（黑马 vueShop 电商后台的接口服务，本地部署在 8888 端口）
#
# ⚠️ 结尾【不要】带斜杠！原因：
#    Excel 里 path 字段自带前导斜杠（如 /login、/users），
#    如果 BASE_URL 结尾也写斜杠，就会拼出 http://...v1//login 这种双斜杠地址。
#    Express 服务端里 //login 不会被字面路径路由 app.use('/api/private/v1/login')
#    匹配到，而是被通配鉴权中间件 app.use('/api/private/v1/*', tokenAuth) 截走，
#    于是【所有】接口统一返回 {"msg":"无效token","status":400} ——
#    这就是之前"全部无效token"问题的根因之一。
# ------------------------------------------------------------------------------
BASE_URL = "http://127.0.0.1:8888/api/private/v1"

# 启动时读一次 Excel，得到所有待执行的用例（列表里每个元素是一条用例的 dict）
data = read_excel()

# ------------------------------------------------------------------------------
# 全局变量池（用例间传参的核心）
#   key   ：变量名，对应 Excel 里写 {{变量名}} 的占位符（如 token、JAY_ID）
#   value ：由"json提取"或"数据库提取"步骤存进来的真实值
# 例如第 1 条登录用例执行后，这里会是 all = {"token": "Bearer eyJxxx..."}
# 之后第 3 条用例的请求头 {"Authorization":"{{token}}"} 渲染时就能取到真值。
# 注意：Python 从上往下执行到这里时它还是空的，是随着用例逐条执行逐步填充的。
# ------------------------------------------------------------------------------
all = {}


class TestRunner:
    """
    测试执行类。

    pytest 的规则：以 Test 开头的类、以 test 开头的方法会被自动识别收集。
    这里把所有用例都汇聚到 test_login 一个方法里，
    靠 @parametrize 参数化让"每条 Excel 数据 = 一次独立执行"。
    """

    # 参数化：pytest 会把 data 列表里的每一条用例 dict 依次传给 case 参数，
    # 生成 6 个独立测试项（case0~case5），报告里一行一条。
    @pytest.mark.parametrize("case", data)
    def test_login(self, case):

        # ======================================================================
        # ① 模板渲染（解决用例依赖）
        # ======================================================================
        # Excel 里写的是字符串，如：
        #   headers = '{"Authorization":"{{token}}"}'
        #   path    = '/users/{{JAY_ID}}/state/true'
        # str(case) 把整个用例 dict 转成字符串 → Template().render(all) 把里面
        # 所有 {{xxx}} 占位符替换成全局变量池 all 里的值（未定义的会替换成空串）
        # → eval() 再把渲染后的字符串还原回 dict。
        # ⚠️ 执行顺序很重要：Excel 里登录用例必须排在最前面，先提取出 token，
        #    后面的用例渲染时才有值可用。
        case = eval(Template(str(case)).render(all))

        # ======================================================================
        # ② Allure 报告动态打标（只影响报告展示，不影响测试逻辑）
        # ======================================================================
        # 用 Excel 的 feature/story/title 列，动态生成报告的三级目录和用例名。
        # "dynamic" 表示运行时打标（因为数据来自参数化，写代码时不知道内容）。
        allure.dynamic.feature(case["feature"])   # 一级模块：如"用户管理"
        allure.dynamic.story(case["story"])       # 二级场景：如"查询成功"
        allure.dynamic.title(f"{case['id']}--{case['title']}")  # 用例标题

        # ======================================================================
        # ③ 从用例 dict 里取请求参数
        # ======================================================================
        method = case["method"]  # 请求方法：get/post/put...

        # 拼接完整 URL。
        # lstrip("/") 先去掉 path 可能带的前导斜杠，再统一由这里补一个"/"，
        # 双保险避免拼出 //login 双斜杠（双斜杠=被服务端鉴权中间件截走，见 BASE_URL 注释）。
        url = f"{BASE_URL}/{str(case['path']).lstrip('/')}"

        # 下面 5 行都是同一个套路：
        #   Excel 单元格里存的是【字符串】形式的 Python 表达式，如 '{"pagenum": 1}'，
        #   isinstance 判断是字符串才 eval 转成真正的 dict；空单元格(None)就保持 None。
        #   这样 requests.request() 收到的要么是 dict 要么是 None，格式统一。
        headers = eval(case["headers"]) if isinstance(case["headers"], str) else None   # 请求头（token 放这里）
        json_body = eval(case["json"]) if isinstance(case["json"], str) else None       # JSON 请求体
        form_data = eval(case["data"]) if isinstance(case["data"], str) else None       # 表单请求体
        params = eval(case["params"]) if isinstance(case["params"], str) else None     # URL 查询参数 ?a=1&b=2
        files = eval(case["files"]) if isinstance(case["files"], str) else None        # 上传文件（文件上传用例用）

        # ======================================================================
        # ④ 组装并发送请求
        # ======================================================================
        # 把所有参数打包成一个 dict，再 **request_data 解包传给 requests，
        # 等价于 requests.request(method=..., url=..., headers=..., json=...)。
        # 好处：不用写 if/else 分支去区分 GET/POST/带不带体，统一一套代码。
        # 注意：json 和 data 传了 None 会被 requests 自动忽略，互不影响。
        request_data = {
            "method": method,
            "url": url,
            "headers": headers,
            "json": json_body,
            "data": form_data,
            "params": params,
            "files": files,
        }
        res = requests.request(**request_data)  # res 是响应对象
        print(res.json())  # 打印响应，配合 -s 选项在控制台可见，方便调试

        # ======================================================================
        # ⑤ HTTP 响应断言（判断用例"真正"过没过的关键！）
        # ======================================================================
        # 两种断言模式，由 Excel 的"检验字段"列决定：
        #   ● 填了 jsonpath（如 $..msg）：精确断言
        #       jsonpath.jsonpath(响应, "$..msg") 返回【列表】（取不到返回 False），
        #       [0] 取第一个匹配值作为"实际结果"，和"预期结果"列做相等比较。
        #       $..msg 的含义：$ 从根开始，.. 递归向下找所有叫 msg 的键。
        #   ● 检验字段为空：模糊断言，直接判断预期文本是否出现在响应原文里。
        # ⚠️ 历史教训：这段 assert 之前整块被注释掉，方法里没有任何断言，
        #    pytest 对"没有断言"的用例默认判 PASSED —— 于是接口明明返回
        #    "无效token"，用例却全部显示通过（假通过）。断言绝不能少！
        if case["check"]:
            actual = jsonpath.jsonpath(res.json(), case["check"])[0]
            assert actual == case["expected"], f"预期[{case['expected']}]，实际[{actual}]，响应：{res.json()}"
        else:
            assert case["expected"] in res.text, f"预期[{case['expected']}]，实际响应：{res.text}"

        # ======================================================================
        # ⑥ 数据库断言（可选：验证接口是否真正写库成功）
        # ======================================================================
        # 当 Excel 里"sql检验"和"sql预期"两列都填了才执行。
        # 典型场景：创建用户接口返回"创建成功"，但到底有没有真插进数据库？
        # 执行 sql_check 里的 SELECT，取第一行第一列和预期值比对。
        # ⚠️ 历史教训：这里查库结果原来也叫 res，会把上面的响应对象覆盖掉，
        #    后面"json提取"再调 res.json() 就报错 —— 所以改名 db_result。
        if case["sql_check"] and case["sql_excepted"]:
            conn = pymysql.Connect(
                host="127.0.0.1",
                port=3306,
                database="mydb",     # vueShop 项目的库名
                user="root",
                password="123456",   # 本机 MySQL 密码
                charset="utf8",
            )
            cur = conn.cursor()          # 拿到游标（执行 SQL 用）
            cur.execute(case["sql_check"])  # 执行 Excel 里写的 SELECT 语句
            db_result = cur.fetchall()   # 取全部结果：((值1, ...), ...) 嵌套元组
            cur.close()                   # 游标和连接都要关，避免连接泄漏
            conn.close()
            # db_result[0][0] = 第一行第一列 = SELECT 出来的那个数
            assert db_result[0][0] == case["sql_excepted"]

        # ======================================================================
        # ⑦ JSON 提取（把响应里的值存入全局变量池，给后续用例用）
        # ======================================================================
        # Excel 里 json提取 列写的是：{"token":"$..token"}
        # 含义：把响应里 jsonpath $..token 匹配到的值，以 key "token" 存进 all。
        # 这样后面用例的 {{token}} 占位符在 ① 步渲染时就能取到真值。
        # ⚠️ 历史教训：这行原来被注释，导致存进 all 的是 "$..token" 这个
        #    表达式字符串本身（而不是表达式的值），后续渲染等于没提取。
        if case["jsonExData"]:
            for key, value in eval(case["jsonExData"]).items():
                # 真正把提取到的值放进变量池
                all[key] = jsonpath.jsonpath(res.json(), value)[0]

        # ======================================================================
        # ⑧ 数据库提取（可选：从数据库取值存入全局变量池）
        # ======================================================================
        # 和 ⑦ 同理，只是数据来源从 HTTP 响应换成 SQL 查询结果。
        # Excel 里 sql提取 列写的是：{"JAY_ID":"SELECT id FROM users WHERE username='hhj'"}
        # 典型场景：创建用户后用例里拿不到新用户 id，就从库里查出来存成 JAY_ID，
        # 后面"修改用户状态"用例的 path /users/{{JAY_ID}}/state/true 就能用上。
        if case["sqlExData"]:
            for key, value in eval(case["sqlExData"]).items():
                conn = pymysql.Connect(
                    host="127.0.0.1",
                    port=3306,
                    database="mydb",
                    user="root",
                    password="123456",
                    charset="utf8",
                )
                cur = conn.cursor()
                cur.execute(value)           # 执行 Excel 里写的 SELECT
                db_result = cur.fetchall()   # 取结果
                cur.close()
                conn.close()
                all[key] = db_result[0]      # 存第一行（元组）进变量池
