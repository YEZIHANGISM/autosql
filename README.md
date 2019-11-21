# autosql
一键生成SQL脚本

# 支持的数据库
Oracle；MySQL；PostgreSQL

# 支持的操作
建表；建索引；删除表

# 安装

        pip install autosql

# 如何使用

        # test.py
        from autosql import autosql

        obj = autosql.get("path\to\excel\", file_name, dbtype, ifdrop, transform)
        obj.create_table()
        obj.create_index()
        obj.drop_table()

# autosql.get()
参数：

1. path: excel文件的路径

2. file_name: 文件名

3. dbtype: 数据库名

4. ifdrop: 是否生成drop语句

5. transform: 是否进行格式转换

# EXCEL文件的格式规范
主要的sheet
1. 目录
        
        示例：
        
        中文名 | 表名 | 是否生成脚本 | 日期分区
        测试表 | Test | 1           | 0

2. 索引

        示例：
        