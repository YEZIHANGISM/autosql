import os


FILE_DIR = os.path.join(os.path.dirname(__file__), 'files')

FILE_NAME = "测试数据字典.xlsx"

STATIC_URL = os.path.join(FILE_DIR, FILE_NAME)

# 数据库类型
DBTYPE = "mysql"

# 是否添加drop语句删除已存在的表
IFDROP = True