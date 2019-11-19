# import xlrd
import pandas as pd
from settings import *
import numpy as np
import re


class CreateSQL:
    # def __init__(self):
    #     self.workbook = xlrd.open_workbook(FILE_DIR+FILE_NAME)

    def _sql_comment(self, info:pd.DataFrame, data:pd.DataFrame):
        n = data.shape[0]
        ch_name = info.at[0, "中文名"]
        tablename = info.at[0, "表名"]
        sqlcomment = "comment on table {} is '{}';\n".format(tablename, ch_name)
        for i in range(1,n):
            field = data.at[i, "字段"]
            sign = data.at[i, "含义"]
            sqlcomment += "comment on column {}.{} is '{}';\n".format(tablename, field, sign)

        return sqlcomment

    def _sql_body(self, data: pd.DataFrame):

        n = data.shape[0]
        sqlbody = ""
        fields = []
        for i in range(n):
            field = data.at[i,"字段"]
            sign = data.at[i,"含义"]
            ftype = data.at[i,"类型"]
            null = data.at[i,"非空"]
            default = data.at[i,"默认值"]
            key = data.at[i, "键"]
            extra = data.at[i, "扩展"]
            if DBTYPE.upper() =="MYSQL":
                fieldline = " ".join(["   ", field, ftype, default, key, extra, null, sign])
            else:
                fieldline = " ".join(["   ", field, ftype, default, null])
            fields.append(fieldline)
        sqlbody += ",\n".join(fields)
        sqlbody += "\n);\n"
        return sqlbody

    def _format_data(self, data: pd.DataFrame):
        n = data.shape[0]
        
        if DBTYPE.upper() == "MYSQL":
            '''字段格式化为小写，加上``'''
            for i in range(n):
                data.at[i,"字段"] = "`{}`".format(data.at[i,"字段"].lower())
                # if data.at[i,"类型"].lower() == "integer":
                #     data.at[i,"类型"] = "int"
                # nan值判断
                if data.at[i,"含义"] == data.at[i,"含义"]:
                    data.at[i,"含义"] = "comment '{}'".format(data.at[i,"含义"])
                else:
                    data.at[i,"含义"] = ""
                data.at[i,"非空"] = "not null" if data.at[i,"非空"] else("null" if data.at[i,"非空"]!=data.at[i,"非空"] else "")
                data.at[i,"默认值"] = "default {}".format(data.at[i,"默认值"]) if data.at[i,"默认值"]==data.at[i,"默认值"] else ""
                data.at[i,"键"] = "" if data.at[i,"键"]!=data.at[i,"键"] else data.at[i,"键"]
                data.at[i,"扩展"] = "" if data.at[i,"扩展"]!=data.at[i,"扩展"] else data.at[i,"扩展"]
        
        elif DBTYPE.upper() == "ORACLE":
            '''oracle表名和字段名在创建时自动转化为大写'''
            for i in range(n):
                varchar = re.match(r'^[v|V]\w+', data.at[i, "类型"])
                if varchar:
                    data.at[i, "类型"] = re.sub(varchar.group(), "VARCHAR2", data.at[i, "类型"])
                if data.at[i, "类型"].upper() in ["DATE", "DATETIME"]:
                    data.at[i, "类型"] = "DATE"
                if data.at[i, "默认值"] != data.at[i, "默认值"]:
                    data.at[i, "默认值"] = ""
                elif data.at[i, "默认值"] == "now()":
                    data.at[i, "默认值"] = "default sysdate"
                # elif data.at[i, "默认值"] != data.at[i, "默认值"]:
                #     data.at[i, "默认值"] = ""
                else:
                    data.at[i, "默认值"] = "default {}".format(data.at[i, "默认值"])
                data.at[i,"非空"] = "not null" if data.at[i,"非空"] else("null" if data.at[i,"非空"]!=data.at[i,"非空"] else "")
        else:
            print("未知的数据库类型")

    def _drop_sql(self, info: pd.DataFrame):
        if DBTYPE.upper() == "MYSQL":
            sqldrop = "drop table if exists %s;\n"%info["表名"][0]
        elif DBTYPE.upper() == "ORACLE":
            sqldrop = '''
declare num number;
begin
    select count(1) into num from user_tables where table_name = upper('%s');
    if num > 0 then
        execute immediate 'drop table %s';
    end if;
end;
/
'''%(info["表名"][0], info["表名"][0])

        return sqldrop

    def _create_sql_str(self, info: pd.DataFrame, data: pd.DataFrame):
        '''
        create sql str
        rtype: string
        '''
        tablename = info.at[0, "表名"]
        pk = info.at[0,"主键"]
        ch_name = info.at[0,"中文名"]
        partition = info.at[0,"日期分区"]
        
        # 根据数据库不同，格式化表格数据
        self._format_data(data)

        # 删除
        sql = self._drop_sql(info) if IFDROP else ""

        '''
        建表
        pgsql对表名、字段名大小写敏感，创建时自动转化为小写
        如果不想转换，需要对字段名加""
        '''
        sql += "create table " + tablename + '(\n'
        print(data)
        sql += self._sql_body(data)
        if DBTYPE.upper() != "MYSQL":
            sql += self._sql_comment(info, data)

        return sql


    def create_table_sql(self):
        '''create table sql and export .sql file'''

        catalog = pd.read_excel(STATIC_URL, sheet_name="目录")
        catalog = catalog[catalog["是否生成脚本"]==1]
        titles = catalog.columns.values     # 获取列名
        cols = catalog.shape[1]             # 获取行数
        rows = catalog.shape[0]             # 获取列数
        content = catalog.values            # 获取所有内容，rtype: ndarray
        colx = catalog.iloc[0].values       # 获取第一行的内容
        colx = catalog.iloc[0, :]
        col_slice = catalog.iloc[:, 2:4]    # 获取第2-4列的所有行内容
        rowx = catalog.sample(1).values     # 获取前N行的内容
        nan = np.isnan(colx[2])             # 判断值是否为nan
        tables = catalog["表名"].values
        cell = catalog.at[0,"是否生成脚本"]  # 取单值
        cell = catalog.iat[0,0]             # 取单值，只能以数字为下标索引   

        # 创建sql语句
        sql = ""
        for i in range(rows):
            info = catalog[:i+1]
            table_content = pd.read_excel(STATIC_URL, sheet_name=tables[i])
            # return table_content
            if table_content.empty:
                print("表 %s 读取失败"%tables[i])
            sql += self._create_sql_str(info, table_content)
        
        # 保存到.sql文件中
        # 如果目录不存在则创建
        save_dir = os.path.join(RESULT_DIR, DBTYPE.upper())
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        with open(os.path.join(save_dir, "create_table.sql"), "w", encoding='utf-8') as f:
            f.write(sql)
            return sql

    def create_index_sql(self):
        index = pd.read_excel(STATIC_URL, sheet_name="索引")

    def drop_table_sql(self):
        catalog = pd.read_excel(STATIC_URL, sheet_name="目录")


csql = CreateSQL()
table_sql = csql.create_table_sql()
print(table_sql)
# index_sql = csql.create_index_sql
# drop_sql = csql.drop_table_sql
