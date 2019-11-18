# import xlrd
import pandas as pd
from settings import *
import numpy as np


class CreateSQL:
    # def __init__(self):
    #     self.workbook = xlrd.open_workbook(FILE_DIR+FILE_NAME)

    def _sql_body(self, data):
        

    def _format_data(self, data):
        pass

    def _drop_sql(self, data: pd.DataFrame):
        pass

    def _create_sql_str(self, info: pd.DataFrame, data: pd.DataFrame):
        '''
        create sql str
        rtype: string
        '''
        
        tablename = info["表名"][0]
        pk = info["主键"][0]
        ch_name = info["中文名"][0]
        partition = info["日期分区"][0]
        
        '''根据数据库不同，格式化表格数据'''
        self._format_data(data)

        # 删除
        sql = self._drop_sql(data) if IFDROP else ""

        # 建表
        '''
        pgsql对表名、字段名大小写敏感，创建时自动转化为小写
        如果不想转换，需要对字段名加""
        '''
        sql += "create table " + tablename + ' /* '+ ch_name +' */'

        sql += self._sql_body(data)


    def create_table_sql(self):
        '''create table sql and export .sql file'''

        catalog = pd.read_excel(STATIC_URL, sheet_name="目录")
        catalog = catalog[catalog["是否生成脚本"]==1]
        titles = catalog.columns.values     # 获取列名
        cols = catalog.shape[1]             # 获取行数
        rows = catalog.shape[0]             # 获取列数
        content = catalog.values            # 获取所有内容，rtype: ndarray
        colx = catalog.iloc[0].values       # 获取第一行的内容
        rowx = catalog.sample(1).values     # 获取前N行的内容
        nan = np.isnan(colx[2])             # 判断值是否为nan
        tables = catalog["表名"].values
        
        # return rows
        sql = ""
        for i in range(rows):
            info = catalog[:i+1]
            table_content = pd.read_excel(STATIC_URL, sheet_name=tables[i])
    
            if table_content.empty:
                print("表%s读取失败"%tables[i])
            sql += self._create_sql_str(info, table_content)
        
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