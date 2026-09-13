# -*- coding: utf-8 -*-
"""
================================================================================
 文件上传用例的手写草稿（学习用参考代码，已被数据驱动方案取代）
================================================================================
 这是最初"手写死"的文件上传脚本草稿，全部注释掉了，仅留作参考对照。

 它演示了文件上传的两步逻辑：
   ① 先登录拿 token（requests 传 data 表单 + 取 data.token）
   ② 再带着 Authorization 头上传文件：
      files={"file":("文件名", 文件对象, "MIME类型")}
      三元组含义 = (上传后的文件名, open()打开的二进制内容, 文件类型)

 现在文件上传已并入数据驱动框架，不需要这个文件了：
   ● Excel 第 6 条用例：files 列写 {"file":("1.png",open("./file/1.png","rb"),"image/png")}
   ● test_runner.py 里的 eval(case["files"]) 会把它还原成三元组传给 requests
 提示：若取消注释单独运行，注意文件扩展名要和 ./file/ 下实际文件一致。
================================================================================
"""

# import requests
#
# login_data = {
#     "method": "post",
#     "url": "http://127.0.0.1:8888/api/private/v1/login",
#     "data": {"username": "admin", "password": "123456"}
# }
# upload_data = {
#     "method": "post",
#     "url": "http://127.0.0.1:8888/api/private/v1/upload",
#     "data": {"username": "admin", "password": "123456"},
#     "headers": None,
#     "files": {"file":("1.jpg",open("./file/1.jpg","rb"),"jpg")}
# }
# res1=requests.request(**login_data)
# token=res1.json()["data"]["token"]
# print(token)
#
# upload_data["headers"]={"Authorization": token}
# res2=requests.request(**upload_data)
# print(res2.json())