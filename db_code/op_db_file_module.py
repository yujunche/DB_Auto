#!/usr/bin/env python
# -*- coding:utf-8 -*-
import cx_Oracle
import pymysql
import os
import time,re
import logging
from bk_manage import models

env_info = 'uat'
oracle_env_ip = models.oracle_db_info.objects.filter(env_info=env_info).get().env_ip
oracle_env_port = models.oracle_db_info.objects.filter(env_info=env_info).get().env_port
oracle_env_sid = models.oracle_db_info.objects.filter(env_info=env_info).get().env_sid


BaseTmpFileD = os.getcwd() + os.sep + 'tmpfile'
BaseFileD = os.getcwd() + os.sep + 'file'
BaseAuditFileD = os.getcwd() + os.sep + 'AuditFile'
BaseAuditRecordFileD = os.getcwd() + os.sep + 'AuditResultFile'

global DML
DML = ['INSERT','DELETE','UPDATE']
global DDL
DDL = ['GRANT','CREATE','ALTER','DROP','COMMENT','DENY','REVOKE']
global NotAllowExec
NotAllowExec = ['DELETE','GRANT','CREATE','ALTER','DROP','COMMENT','DENY','REVOKE']
global  ALLTYPE
ALLTYPE = ['INSERT','DELETE','UPDATE','GRANT','CREATE','ALTER','DROP','COMMENT','DENY','REVOKE']

class Oracle_op(object):
    def __init__(self, db_user_name, password):
        self.db_user_name = db_user_name
        self.password = password
        self.dsn = '%s:%s/%s'%(oracle_env_ip,oracle_env_port,oracle_env_sid)
        self.orcl_db = cx_Oracle.connect(
            user=self.db_user_name,password=self.password,dsn=self.dsn)

    def exec_oracle(self, sql_input_oracle):
        cursor = self.orcl_db.cursor()
        sql_input_oracle = sql_input_oracle.rstrip().rstrip(';')
        if sql_input_oracle.lower().find('update') != -1:
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            rownum = cursor.rowcount
            db_message = db_op_message + '%s行已更新' % rownum + ';' + '\n'
            return db_message
        elif sql_input_oracle.lower().find('insert') != -1:
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            rownum = cursor.rowcount
            db_message = db_op_message + '%s行已插入' % rownum + ';' + '\n'
            return db_message
        elif sql_input_oracle.lower().find('delete') != -1:
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            rownum = cursor.rowcount
            db_message = db_op_message + '%s行已删除' % rownum + ';' + '\n'
            return db_message
        elif sql_input_oracle.lower().find('grant') != -1:
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            db_message = db_op_message + 'grant 成功' + ';' + '\n'
            return db_message
        elif len(re.compile('create\s*table').findall(sql_input_oracle.lower())):
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            db_message = db_op_message + 'create table 成功' + ';' + '\n'
            return db_message
        elif len(re.compile('alter\s*table').findall(sql_input_oracle.lower())):
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            db_message = db_op_message + 'alter table 成功' + ';' + '\n'
            return db_message
        elif len(re.compile('create.*synonym').findall(sql_input_oracle.lower())):
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            db_message = db_op_message + 'create synonym 成功' + ';' + '\n'
            return db_message
        elif len(re.compile('create\s*index').findall(sql_input_oracle.lower())):
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            db_message = db_op_message + 'create index 成功' + ';' + '\n'
            return db_message
        elif len(re.compile('drop\s*index').findall(sql_input_oracle.lower())):
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            db_message = db_op_message + 'drop index 成功' + ';' + '\n'
            return db_message
        elif len(re.compile('create\s*unique\s*index').findall(sql_input_oracle.lower())):
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            db_message = db_op_message + 'create unique index 成功' + ';' + '\n'
            return db_message
        elif sql_input_oracle.lower().find('comment') != -1:
            cursor.execute(sql_input_oracle)
            db_op_message = ''
            db_message = db_op_message + 'comment 成功' + ';' + '\n'
            return db_message
        elif len(re.compile('^\s*--').findall(sql_input_oracle.lower())):
            db_op_message = ''
            db_message = db_op_message + sql_input_oracle + ';' + '\n'
            return  db_message
        else:
            db_op_message = ''
            db_op_message = db_op_message + '输入sql有误' + ';' + '\n'
            return db_op_message
        cursor.close()

    def commit_oracle(self):
        self.orcl_db.commit()
        return '提交完成'

    def rollback_oracle(self):
        self.orcl_db.rollback()
        return '回滚完成'

    def close_connect(self):
        self.orcl_db.close()
        return '数据库连接已经关闭'


# from bk_manage import models
#
# db_exec_map = {}
# for i in models.oracle_db_user_info.objects.all():
#     username = i.username
#     db_exec = Oracle_op(username, models.oracle_db_user_info.objects.filter(
#         username=username).get().password)
#     db_exec_map[username] = db_exec
# print(db_exec_map)
#
#
# def get_db_exec_map(user):
#     return db_exec_map[user]

# create global dictionary
global db_exec_map
db_exec_map = {}

global db_audit_map
db_audit_map = {}


### mysql --> ORM
class mysql_op(object):
    def __init__(self, db_user_name, password):
        self.mysql_username = mysql_env_user
        self.mysql_passwd = mysql_env_passwd
        self.mysql_ip = mysql_env_ip
        self.mysql_db_name = mysql_env_db
        self.mysql_db = pymysql.connect(
            '%s,%s,%s,%s' % (self.mysql_ip, self.mysql_username, self.mysql_passwd, self.mysql_db_name))
        # self.mysql_db = cx_Oracle.connect('%s/%s@%s:%s/%s'%(self.db_user_name,self.password,env_ip,env_port,env_sid))

    def record_oracle(self, sql_input_mysql):
        cursor = self.mysql_db.cursor()
        mysql_sql_exec = sql_input_mysql.rstrip().rstrip(';')
        try:
            cursor.execute(mysql_sql_exec)
        except cx_Oracle.DatabaseError as db_error:
            return db_error
        else:
            rownum = cursor.rowcount
            if rownum != 0:
                return 'sql记录已经执行'
        cursor.close()

    def sel_record_oracle(self, sel_record_audit):
        # exec_sel_record_audit = 'select * from db_op where status=1 '
        cursor = self.mysql_db.cursor()
        cursor.execute(sel_record_audit)
        data = cursor.fetchall()
        sel_message = ''
        for list_row_input in data:
            sel_message = sel_message + list_row_input + '\n'
        return sel_message
        cursor.close()

    def commit_mysql(self):
        self.mysql_db.commit()
        return 'sql记录已经提交'

    def rollback_mysql(self):
        self.mysql_db.rollback()
        return 'sql记录已经回滚'

    def close_connect_mysql(self):
        self.mysql_db.close()
        return 'mysql数据库连接已经关闭'


def tmp_file_create(tmp_file_name):
    tmp_dir = BaseTmpFileD + os.sep + time.strftime("%Y%m%d")
    tmp_file = tmp_dir + os.sep + tmp_file_name
    if os.path.isdir(tmp_dir):
        pass
    else:
        os.makedirs(tmp_dir)
    if os.path.isfile(tmp_file):
        pass
    else:
        f = open('%s' % tmp_file, 'w', encoding="utf-8")
        f.close()
    return tmp_file


def tmp_file_write(tmp_file_name, tmp_file_data):
    #tmp_file = BaseTmpFileD + os.sep + tmp_file_name
    # print('tmpfile',tmp_file_data)
    with open(tmp_file_name, 'a+', encoding="utf-8") as f:
        f.write(tmp_file_data + '\n')


def tmp_file_clean(tmp_file):
    # tmp_file = BaseTmpFileD + os.sep + tmp_file_name
    with open('%s' % tmp_file, 'w+', encoding="utf-8") as f:
        f.truncate()


def tmpfile_rewrite(tmp_file_name, file_name):
    #if os.path.isdir(BaseFileD):
    #    pass
    #else:
    #    os.makedirs(BaseFileD)
    f = open(tmp_file_name, 'r', encoding="utf=8")
    f_rewrite = open(file_name, 'a+', encoding="utf=8")
    for line in f:
        f_rewrite.write(line)
    f.close()
    f_rewrite.close()

def Audit_Record_write(AudifFileName,AuditResultRecord):
    if os.path.isdir(BaseAuditRecordFileD):
        pass
    else:
        os.makedirs(BaseAuditRecordFileD)
    ##多次审批，每次清空文件
    #with open(AudifFileName, 'w+', encoding="utf-8") as f:
    #    f.truncate()
    with open(AudifFileName,'a+',encoding="utf-8") as f:
        f.write(AuditResultRecord)