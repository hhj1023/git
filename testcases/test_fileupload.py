# -*- coding: utf-8 -*-
"""文件上传用例手写草稿（学习参考，已被数据驱动方案取代，见 test_runner.py 的 files 列）"""

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
