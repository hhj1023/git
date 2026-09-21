# 接口自动化测试项目（pytest + requests）

基于 **pytest + requests** 的 Excel 数据驱动接口自动化测试框架，覆盖 **登录、用户管理、商品管理、图片上传、权限管理、订单管理、角色管理、异常参数、重复提交** 9 个模块共 **40 条用例**，支持 **HTTP 断言 + 数据库断言**、JSON/JDBC 变量提取与用例间传参，执行后一键生成 Allure 可视化报告。

除正向业务流程外，还覆盖**鉴权失败、参数缺失/类型错误/取值越界**等异常场景，以及**重复提交**的幂等性与重名校验验证（其中角色重复提交为已确认的服务端缺陷，见用例 34）。

## 技术栈

| 分类 | 技术 |
|---|---|
| 语言 | Python 3.13 |
| 测试框架 | pytest（参数化、夹具、pytest.ini 统一配置） |
| 请求发送 | requests |
| 数据驱动 | openpyxl（Excel）+ Jinja2（变量渲染） |
| 数据提取 | jsonpath（响应提取）、pymysql（数据库提取） |
| 测试报告 | allure-pytest（三级目录 + 步骤 + 附件） |
| 日志 | logging（CLI 实时日志 + 文件日志） |

## 项目结构

```
test_project/
├── run.py                  # 测试入口：一键执行用例并生成 Allure 报告
├── pytest.ini              # pytest 配置（日志格式、日志文件）
├── config/
│   └── config.py           # 环境配置（服务地址、Excel 路径、数据库连接）
├── testcases/
│   └── test_runner.py      # 用例执行器（框架核心）
├── data/
│   └── 测试数据.xlsx        # 测试用例（数据驱动）
├── utils/
│   ├── excel_utils.py      # 读取 Excel 用例
│   ├── analyse_case.py     # 解析请求数据并组装 URL/参数
│   ├── send_request.py     # 发送 HTTP 请求 / JDBC 查询
│   ├── asserts.py          # HTTP 断言 + 数据库断言
│   ├── extractor.py        # JSON 提取 + JDBC 提取
│   └── allure_utils.py     # Allure 报告动态打标
├── file/                   # 图片上传用例的测试附件
├── log/                    # 运行日志
└── report/                 # 测试报告（已 gitignore）
```

## 核心设计

**1. Excel 数据驱动，用例与代码分离**
所有用例以行为单位存放在 `data/测试数据.xlsx`，字段包含请求方式、路径、请求头、params / json / data / files 参数、校验字段、预期结果、数据库校验、提取表达式、是否执行。新增或调整用例无需改动代码；`is_true` 列可直接临时禁用某条用例。

**2. Jinja2 变量池解决用例间依赖**
用例中可用 `{{token}}`、`{{JAY_ID}}`、`{{SHOP_ID}}` 等占位符引用前序用例提取的值。执行时通过 Jinja2 渲染 + `eval` 还原为 dict，实现「登录拿到 token → 后续用例自动带上」「创建用户拿到 ID → 修改/删除复用」。

**3. 双层断言：HTTP 断言 + 数据库断言**
- HTTP 断言：优先用 jsonpath 精确比对字段值，无 jsonpath 时退化为响应文本模糊匹配；
- **JDBC 断言**：直接查库校验接口是否真正写库成功（如新增用户后校验 `user_name` 是否落库），避免「接口返回成功但数据没落库」的漏测。

**4. 提取器：接口间数据传递**
支持 jsonpath 从响应中提取（如 `$..token`）和 SQL 从数据库提取（如新用户 ID），统一存入全局变量池供后续用例渲染使用。

**5. Allure 报告**
动态标注 `feature / story / title` 形成三级目录，`@allure.step` 展示「解析请求数据 → 发送请求 → 断言 → 提取」完整步骤，请求数据以附件形式记录，失败可定位到具体参数。

**6. 幂等设计（可重复执行）**
用户、商品用例均采用「创建 → 修改 → 删除」闭环，测试数据自动清理；商品删除为软删除且 `goods_name` 有唯一索引，因此商品名使用 `{{now}}`（运行时间戳）动态生成，保证反复执行不冲突，**重跑无需手动清库**。

**7. 日志**
`pytest.ini` 统一配置，CLI 实时输出 + `log/` 文件落盘，格式含文件名、方法名、行号、日志级别，便于问题回溯。

## 用例清单

| 编号 | 模块 | 场景 | 请求 | 说明 |
|---|---|---|---|---|
| 1 | 登录 | 登录成功 | POST /login | 提取 token，校验数据库登录信息 |
| 2 | 用户管理 | 未登录查询失败 | GET /users | 无 token 鉴权失败场景 |
| 3 | 用户管理 | 查询成功 | GET /users | 查询用户列表 |
| 4 | 用户管理 | 创建成功 | POST /users | 提取新用户 ID 供后续用例复用 |
| 5 | 用户管理 | 修改成功 | PUT /users/{{JAY_ID}}/state/true | 使用提取的 ID 修改状态 |
| 6 | 用户管理 | 删除成功 | DELETE /users/{{JAY_ID}} | 使用提取的 ID 删除，闭环清理 |
| 7 | 图片上传 | 上传成功 | POST /upload | 上传 png 附件，校验返回地址 |
| 8 | 商品管理 | 查询成功 | GET /goods | 查询商品列表 |
| 9 | 商品管理 | 创建成功 | POST /goods | 商品名动态生成，提取商品 ID |
| 10 | 商品管理 | 修改成功 | PUT /goods/{{SHOP_ID}}/state/1 | 使用提取的 ID 修改状态 |
| 11 | 商品管理 | 删除成功 | DELETE /goods/{{SHOP_ID}} | 使用提取的 ID 删除，闭环清理 |
| 12 | 权限管理 | 查询成功 | GET /rights/list | 权限列表（type 仅支持 list / tree） |
| 13 | 订单管理 | 查询成功 | GET /orders | 提取订单 ID 供后续用例复用 |
| 14 | 订单管理 | 修改成功 | PUT /orders/{{ORDER_ID}} | 订单无 `/state/:state` 路由，直接 PUT 本体 |
| 15 | 角色管理 | 查询成功 | GET /roles | 查询角色列表 |
| 16 | 角色管理 | 创建成功 | POST /roles | 角色名动态生成，提取 roleId |
| 17 | 角色管理 | 修改成功 | PUT /roles/{{ROLES_ID}} | 服务端更新成功返回 msg 为「获取成功」 |
| 18 | 角色管理 | 删除成功 | DELETE /roles/{{ROLES_ID}} | 闭环清理 |
| 19 | 权限管理 | 鉴权失败 | GET /users（无 token） | 提示「无效token」 |
| 20 | 权限管理 | 鉴权失败 | GET /users（错误 token） | 提示「无效token」 |
| 21 | 权限管理 | 查询成功 | GET /rights/tree | 树形结构权限列表 |
| 22 | 权限管理 | 参数非法 | GET /rights/xxx | 提示「显示类型参数错误」 |
| 23 | 权限管理 | 创建成功 | POST /roles | 创建授权专用角色 |
| 24 | 权限管理 | 授权成功 | POST /roles/{{AUTH_ROLE_ID}}/rights | 为角色赋权限 101 |
| 25 | 权限管理 | 取消授权 | DELETE /roles/{{AUTH_ROLE_ID}}/rights/101 | 取消权限成功 |
| 26 | 权限管理 | 删除成功 | DELETE /roles/{{AUTH_ROLE_ID}} | 闭环清理 |
| 27 | 异常参数 | 缺少必填 | GET /orders（无 pagenum） | 提示「pagenum 参数错误」 |
| 28 | 异常参数 | 参数越界 | GET /orders?pagenum=0 | 提示「pagenum 参数错误」 |
| 29 | 异常参数 | 缺少必填 | POST /roles（空 body） | 提示「角色名称不能为空」 |
| 30 | 异常参数 | 类型错误 | PUT /roles/abc | 提示「角色ID必须为数字」 |
| 31 | 异常参数 | 缺少必填 | POST /goods（空 body） | 提示「商品名称不能为空」 |
| 32 | 异常参数 | 缺少必填 | PUT /orders/{{ORDER_ID}} | 缺 order_price，提示「订单价格不能为空」 |
| 33 | 重复提交 | 首次提交 | POST /roles | 创建角色，提取 ID 与名称 |
| 34 | 重复提交 | 重复提交 | POST /roles（同名第二次） | **服务端未校验重名仍返回「创建成功」——已确认缺陷** |
| 35 | 重复提交 | 清理数据 | DELETE /roles/{{DUP_ROLE_ID2}} | 删除重复产生的副本 |
| 36 | 重复提交 | 首次删除 | DELETE /roles/{{DUP_ROLE_ID}} | 删除成功 |
| 37 | 重复提交 | 重复删除 | DELETE /roles/{{DUP_ROLE_ID}} | 第二次提示「删除失败」 |
| 38 | 重复提交 | 首次提交 | POST /goods | 创建商品，提取 ID 与名称 |
| 39 | 重复提交 | 重复提交 | POST /goods（同名第二次） | 商品表有唯一索引，正确拦截：「商品名称已存在」 |
| 40 | 重复提交 | 清理数据 | DELETE /goods/{{DUP_GOODS_ID}} | 闭环清理 |

> 用例 34 当前断言为「创建成功」，即**锁定现状行为**。若后续 `sp_role.role_name` 补上唯一约束，将该用例预期改为「角色名称已存在」，即可直接作为回归验证。

## 运行

```bash
# 1. 安装依赖
pip install pytest requests openpyxl jinja2 jsonpath pymysql allure-pytest

# 2. 配置环境变量（数据库密码不再写死在代码里）
#    Windows(cmd):        set DB_PASSWORD=你的数据库密码
#    Windows(PowerShell): $env:DB_PASSWORD="你的数据库密码"
#    macOS/Linux:         export DB_PASSWORD=你的数据库密码
#    PyCharm:             Run/Debug Configurations -> Environment variables
#    其他可配置项见 .env.example（均有默认值，只有密码必填）

# 3. 启动被测服务（vueShop-api-server，监听 127.0.0.1:8888）

# 4. 执行用例并生成报告
python run.py

# 5. 查看报告
#    浏览器打开 ./report/html_report/index.html
```

> 未配置 `DB_PASSWORD` 时会直接抛出明确提示：用例 1 需要查库校验登录信息，缺密码会导致 token 提取失败、后续用例连锁失败。

### 配置项（全部读环境变量，见 `config/config.py`）

| 变量 | 默认值 | 说明 |
|---|---|---|
| `DB_PASSWORD` | 无（必填） | MySQL 密码，用于数据库断言与提取 |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` | `127.0.0.1` / `3306` / `mydb` / `root` | 数据库连接 |
| `BASE_URL` | `http://127.0.0.1:8888/api/private/v1` | 被测服务地址 |
| `EXCEL_FILE` / `SHEET_NAME` | `./data/测试数据.xlsx` / `Sheet1` | 用例文件 |

## 测试报告

最新运行：**40 条用例全部通过**，9 个业务模块覆盖率 100%，连续多次执行均通过（用例自闭环，重跑无需手动清库）。

| 指标 | 结果 |
|---|---|
| 用例总数 | 40 |
| 通过 / 失败 | 40 / 0（100%） |
| 覆盖模块 | 登录、用户管理、图片上传、商品管理、权限管理、订单管理、角色管理、异常参数、重复提交（9 个） |
| 单次执行耗时 | 约 0.7s |
| 可重复执行 | 是（创建→删除闭环，`{{now}}` 动态数据，重跑无需清库） |

![Allure 测试报告总览](https://raw.githubusercontent.com/hhj1023/git/main/docs/allure-overview.png)

> 这里用绝对地址而非相对路径：相对路径会被 GitHub 渲染成 `raw.githubusercontent.com` 直链，在部分网络环境下该域名无法解析，图片就显示不出来；绝对地址则会走 GitHub 的 `camo.githubusercontent.com` 图片代理，可正常加载。

## 环境要求

- Python 3.8+
- 被测服务：vueShop-api-server（`http://127.0.0.1:8888/api/private/v1`）
- 数据库：MySQL（用于数据库断言与提取），密码通过环境变量 `DB_PASSWORD` 注入
- Allure 命令行工具（用于渲染 HTML 报告）

## 说明

本项目为个人接口自动化学习实践项目，用来练习测试框架的分层设计、数据驱动、断言体系与报告输出。
