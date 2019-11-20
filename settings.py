import os

# 总路径
BASE_DIR = os.path.dirname(__file__)

# 读取文件路径
FILE_DIR = os.path.join(BASE_DIR, 'files')

# 读取文件名
FILE_NAME = "测试数据字典.xlsx"

STATIC_URL = os.path.join(FILE_DIR, FILE_NAME)

# 存储结果目录
RESULT_URL = 'sql'

# 数据库类型
DBTYPE = "oracle"

# 存储结果路径
RESULT_DIR = os.path.join(BASE_DIR, RESULT_URL)

# 是否添加drop语句删除已存在的表
IFDROP = True

# 是否需要转换类型
ISTRANSFORM = True