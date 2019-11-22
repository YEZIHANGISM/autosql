# autosql
一键生成SQL脚本

# 支持的数据库
Oracle; MySQL; PostgreSQL

# 支持的操作
建表；建索引；删除表

# 安装

        pip install autosql

# 使用

        # test.py
        from autosql import autosql

        obj = autosql.get("path\to\excel\", file_name, dbtype, ifdrop, transform)
        obj.create_table()
        obj.create_index()
        obj.drop_table()

# autosql.get()
参数：

1. path: excel文件路径

2. file_name: excel文件名

3. dbtype: 数据库

4. ifdrop: 是否生成drop语句

5. transform: 是否进行格式转换 

# EXCEL格式规范
## sheets
1. 目录
        
        结构：
        
        中文名 | 表名 | 是否生成脚本 | 日期分区
        测试表 | Test | 1           | 0

2. 索引

        示例：
        表名 | 索引列   | 是否主键 | 是否唯一索引 | 是否有效
        Test | isValid | 0       | 0           | 1

3. Test(表名)

        示例:
        字段     | 含义  | 类型 | 非空 | 默认值 | 键          | 扩展
        id       | 标识 | int  | 是   |        | primary key | auto_increment
        initdate | 时间 | Date | 是   | now()  |             |   

## 函数
表中的函数、数据类型、扩展等都默认为mysql格式，或者你可以自行填写，然后将格式转换设置为False，前提是你确保填写正确 

        transform = False

