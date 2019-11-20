# import xlrd
import pandas as pd
from settings import *
import numpy as np
import re


class CreateSQL:
    # def __init__(self):
    #     self.workbook = xlrd.open_workbook(FILE_DIR+FILE_NAME)

    def _save_file(self, sql, filename):
        save_dir = os.path.join(RESULT_DIR, DBTYPE.upper())
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        with open(os.path.join(save_dir, filename), "w", encoding='utf-8') as f:            
            try:
                f.write(sql)
            except Exception as e:
                return e
            else:
                return sql

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

    def _sql_index(self, index:pd.DataFrame):
        '''索引sql'''
        sqlindex = ""
        n = index.shape[0]
        for i in range(n):
            tb_name = index.at[i, "表名"]
            fields = index.at[i, "索引列"]
            pk = index.at[i, "是否主键"]
            uk = index.at[i, "是否唯一索引"]
            
            idxname = "IDX_{}".format(tb_name)
            uidxname = "UIDX_{}".format(tb_name)
            pkname = "PK_{}".format(tb_name)
            if DBTYPE.upper() == "PGSQL":
                if pk == 1:
                    # 主键
                    sqlindex += (
                        "drop index if exists {pkname};\n" \
                        "alter table {tbname} add constraint {pkname} primary key({fields});\r\n".format(pkname=pkname, tbname=tb_name, fields=",".join(fields.split(";")))
                    )
                elif uk == 1:
                    # 唯一索引
                    sqlindex += (
                        "drop index if exists {idxname};\n" \
                        "create unique index {idxname} on (\n" \
                        "{fields}\n" \
                        ");\r\n".format(idxname=uidxname, fields=",\n".join(fields.split(";")))
                    )
                else:
                    # 普通索引
                    sqlindex += (
                        "drop index if exists {idxname};\n" \
                        "create index {idxname} on (\n" \
                        "{fields}\n" \
                        ");\r\n".format(idxname=idxname, fields=",\n".join(fields.split(";")))
                    )
            elif DBTYPE.upper() == "MYSQL":
                '''mysql使用存储过程删除索引'''
                # 创建存储过程
                procedure = "drop_index"
                if i == 0:
                    sqlindex += (
                        "drop procedure if exists {procedure};\n" \
                        "create procedure {procedure}(in tbname varchar(200), in idxname varchar(200))\n" \
                        "begin\n" \
                        "declare str varchar(250);\n" \
                        "if idxname='PRIMARY' then\n" \
                        "   set @str=concat('alter table ', tbname, ' drop primary key');\n" \
                        "else\n" \
                        "   set @str=concat('drop index ', idxname, ' on ', tbname);\n" \
                        "end if;\n" \
                        "select count(*) into @cnt from infomation_schema.statistics where table_name=tbname and index_name=idxname;\n" \
                        "if @cnt > 0 then\n" \
                        "prepare stmt from @str;\n" \
                        "execute stmt;\n" \
                        "end if;\n" \
                        "end;\r\n".format(procedure=procedure)
                    )
                
                if pk == 1:
                    sqlindex += (
                        "call {procedure}('{tbname}', 'PRIMARY');\n" \
                        "alter table {tbname} add primary key({fields});\r\n".format(procedure=procedure, tbname=tb_name, fields=",".join(fields.split(";")))
                    )
                elif uk == 1:
                    sqlindex += (
                        "call {procedure}('{tbname}', '{uidxname}');\n" \
                        "create unique index {uidxname} on {tbname}(\n" \
                        "{fields}\n" \
                        ");\r\n".format(procedure=procedure, tbname=tb_name, uidxname=uidxname, fields=',\n'.join(fields.split(";")))
                    )
                else:
                    sqlindex += (
                        "call {procedure}('{tbname}', '{idxname}');\n" \
                        "create index {idxname} on {tbname}(\n" \
                        "{fields}\n" \
                        ");\r\n".format(procedure=procedure, tbname=tb_name, idxname=idxname, fields=',\n'.join(fields.split(";")))
                    )
            
            elif DBTYPE.upper() == "ORACLE":
                if pk == 1:
                    sqlindex += (
                        "declare num number;\n" \
                        "begin\n" \
                        "   select count(1) into num from user_indexs where index_name = '{idxname}';\n" \
                        "   if num > 0 then\n" \
                        "       execute immediate 'alter table {tbname} drop constraint {pkname}';\n" \
                        "   end if;\n" \
                        "end;\n" \
                        "alter table {tbname} add constraint {pkname} primary key(fields);\r\n" \
                        .format(idxname=idxname, tbname=tb_name, pkname=pkname, fields=",".join(fields.split(";")))
                    )
                    
                elif uk == 1:
                    sqlindex += (
                        "declare num number;\n" \
                        "begin\n" \
                        "   select count(1) into num from user_indexs where index_name = '{uidxname}';\n" \
                        "   if num > 0 then\n" \
                        "       execute immediate 'drop index {uidxname}';\n" \
                        "   end if;\n" \
                        "end;\n" \
                        "create unique index {uidxname} on {tbname}(\n" \
                        "{fields}\n" \
                        ");\r\n" \
                        .format(uidxname=uidxname, tbname=tb_name, fields=",\n".join(fields.split(";")))
                    )
                else:
                    "declare num number;\n" \
                        "begin\n" \
                        "   select count(1) into num from user_indexs where index_name = '{idxname}';\n" \
                        "   if num > 0 then\n" \
                        "       execute immediate 'drop index {idxname}';\n" \
                        "   end if;\n" \
                        "end;\n" \
                        "create index {idxname} on {tbname}(\n" \
                        "{fields}\n" \
                        ");\r\n" \
                        .format(idxname=idxname, tbname=tb_name, fields=",\n".join(fields.split(";")))

        return sqlindex

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
                # if data.at[i,"类型"].upper() == "INTEGER":
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
                # nan
                if data.at[i, "默认值"] != data.at[i, "默认值"]:
                    data.at[i, "默认值"] = ""
                elif data.at[i, "默认值"] == "now()":
                    data.at[i, "默认值"] = "default sysdate"
                else:
                    data.at[i, "默认值"] = "default {}".format(data.at[i, "默认值"])
                data.at[i,"非空"] = "not null" if data.at[i,"非空"] else("null" if data.at[i,"非空"]!=data.at[i,"非空"] else "")
        
        elif DBTYPE.upper() == "PGSQL":
            '''
            postgresql字段在创建时自动转化为小写
            date类型自动转化为timestamp，因为pgsql的date只支持日期
            '''
            for i in range(n):
                if data.at[i, "键"] == "primary key":
                    if data.at[i, "类型"].lower() == "tinyint":
                        data.at[i, "类型"] = "smallserial"
                    elif data.at[i, "类型"].lower() == "bigint":
                        data.at[i, "类型"] = "bigserial"
                    else:
                        data.at[i, "类型"] = "serial"
                
                if data.at[i, '类型'].lower() == "date" or data.at[i, '类型'].lower() == "datetime":
                    data.at[i,"类型"] = "timestamp"
                if data.at[i, "类型"].lower() in ["blob", "clob", "varchar(max)"]:
                    data.at[i, "类型"] = "bytea"
                if data.at[i, "类型"].lower() == "int":
                    data.at[i, "类型"] = 'integer'
                if data.at[i, "类型"].lower() == "tinyint":
                    data.at[i, "类型"] = "smallint"
                if data.at[i, "默认值"] in ["now()", "sysdate", "getdate()"]:
                    data.at[i, "默认值"] = 'localtimestamp'
                elif data.at[i, "默认值"] == data.at[i, "默认值"] and data.at[i, "默认值"] in ["time", "timestamp", "date"]:
                    data.at[i, "默认值"] = "to_date({}, 'yyyy-mm-dd')".format(data.at[i, "默认值"])
                else:
                    data.at[i, "默认值"] = ""
                data.at[i,"非空"] = "not null" if data.at[i,"非空"] else("null" if data.at[i,"非空"]!=data.at[i,"非空"] else "")
        
        else:
            print("未知的数据库类型")

    def _drop_sql(self, info: pd.DataFrame):
        tb_name = info.at[0, "表名"]
        if DBTYPE.upper() == "MYSQL":
            sqldrop = "drop table if exists {tbname};\n".format(tbname=tb_name)
        elif DBTYPE.upper() == "PGSQL":
            sqldrop = "drop table if exists {tbname} cascade;\n".format(tbname=tb_name)
        elif DBTYPE.upper() == "ORACLE":
            sqldrop = (
                "declare num number;\n" \
                "begin\n" \
                "   select count(1) into num from user_tables where table_name = upper({tbname});\n" \
                "if num > 0 then\n" \
                "   execute immediate 'drop table {tbname}';\n" \
                "   end if;\n" \
                "end;\r\n" \
                .format(tbname=tb_name)
            )
        return sqldrop

    def _create_sql_str(self, info: pd.DataFrame, data: pd.DataFrame):
        '''
        create sql str
        rtype: string
        '''
        tablename = info.at[0, "表名"]
        
        # 根据数据库不同，格式化表格数据
        if ISTRANSFORM:
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
        catalog = catalog[catalog["是否生成脚本"]==1].reset_index(drop=True)
        rows = catalog.shape[0]             # 获取列数
        tables = catalog["表名"].values 

        # 创建sql语句
        sql = ""
        for i in range(rows):
            info = catalog[:i+1]
            table_content = pd.read_excel(STATIC_URL, sheet_name=tables[i])
            # return table_content
            if table_content.empty:
                print("表 %s 读取失败"%tables[i])
            sql += self._create_sql_str(info, table_content)
        
        # 覆盖保存到.sql文件中
        return self._save_file(sql, "create_table.sql")
        

    def create_index_sql(self):
        index = pd.read_excel(STATIC_URL, sheet_name="索引")
        index = index[index["是否有效"]==1].reset_index(drop=True)
        sqlindex = self._sql_index(index)
        return self._save_file(sqlindex, "create_index.sql")

    def drop_table_sql(self):
        catalog = pd.read_excel(STATIC_URL, sheet_name="目录")
        sqldrop = self._drop_sql(catalog)

        return self._save_file(sqldrop, "drop_table.sql")


csql = CreateSQL()
create_table_sql = csql.create_table_sql
create_index_sql = csql.create_index_sql
drop_table_sql = csql.drop_table_sql
