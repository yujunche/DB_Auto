#!/usr/bin/env python
# -*- coding:utf-8 -*-

from db_code.op_db_file_module import *
import cx_Oracle
import time, os
import random
import string
from dbaudit import models as Admodels


def generate_random_str(randomlength=16):
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


def judge_op_type(input_sql_type, input_sql):
    if input_sql_type.lower() == 'dml':
        if input_sql.lower().find('alter') != -1 or input_sql.lower().find('create') != -1 or input_sql.lower().find(
                'drop') != -1:
            print('输入的数据库操作语言有误，请检查输入的sql。')
            exit()
        else:
            pass
    elif input_sql_type.lower() == 'ddl':
        if input_sql.lower().find('update') != -1 or input_sql.lower().find('insert') != -1 or input_sql.lower().find(
                'delete') != -1:
            print('输入的数据库操作语言有误，请检查输入的sql。')
            exit()
        else:
            pass
    else:
        print('请输入正确的数据库操作语言dml/ddl。')
        exit()


def execute_oracle_file(**kwargs):
    # judge_op_type(kwargs['input_sql_type'],kwargs['input_sql'])
    # print('exec',kwargs['input_sql'])
    sql_batch = kwargs['input_sql'].rstrip().rstrip(';').split(';')
    db_exec = db_exec_map[kwargs['user']][kwargs['sel_priv']]
    db_record = ''
    for bath_exec in sql_batch:
        try:
            db_msg = db_exec.exec_oracle(bath_exec)
        except cx_Oracle.DatabaseError as orcl_error_msg:
            db_msg = str(orcl_error_msg) + ';' + '\n'
        else:
            # bath_exec = '\n' + bath_exec
            tmp_file_write(kwargs['tmpfilename'], bath_exec)
        db_record = db_record + db_msg
    return db_record


def commit_oracle_file(**kwargs):
    # print('%s_%s_%s.sql'%(kwargs['user'],kwargs['req_no'],time.strftime("%Y%m%d%H%M%S")))
    db_exec = db_exec_map[kwargs['user']][kwargs['sel_priv']]
    db_exec.commit_oracle()
    file_name = '%s_%s_%s.sql' % (kwargs['user'], kwargs['req_no'], time.strftime("%Y%m%d%H%M%S"))
    file_dir = BaseFileD + os.sep + file_name
    tmp_dir = BaseTmpFileD + os.sep + kwargs['tmpfilename']
    if os.path.getsize(tmp_dir) != 0:
        tmpfile_rewrite(tmp_dir, file_dir)
        models.op_oracle_record.objects.create(exec_user=kwargs['user'], req_no=kwargs['req_no'],
                                               stamp=time.strftime("%Y%m%d%H%M%S"), file_dir=file_dir)
        tmp_file_clean(tmp_dir)
    else:
        pass


def rollback_oracle_file(**kwargs):
    db_exec = db_exec_map[kwargs['user']][kwargs['sel_priv']]
    db_exec.rollback_oracle()
    tmp_dir = BaseTmpFileD + os.sep + kwargs['tmpfilename']
    tmp_file_clean(tmp_dir)


def audit_commit(**kwargs):
    # 写入auditfile中，写入mysql数据库审计表中(提交用户，需求号，sql文件路径，审核状态位,问题描述)
    auditfile = '%s_%s_%s.sql'%(kwargs['exec_user'],kwargs['audit_req'],time.strftime("%Y%m%d%H%M%S"))
    auditfiledpath = BaseAuditFileD + os.sep + auditfile
    if os.path.isdir(BaseAuditFileD):
        pass
    else:
        os.makedirs(BaseAuditFileD)
    with open(auditfiledpath,'a+',encoding='utf-8') as f:
        #f.write('--%s \n'%kwargs['query_desc'])
        f.write(kwargs['audit_sql'])
    Admodels.db_audit_record.objects.create(exec_user=kwargs['exec_user'],db_user=kwargs['select_user'],req_no=kwargs['audit_req'],
                                            state='W',file_dir=auditfiledpath,DescMessage=kwargs['query_desc'],stamp=time.strftime("%Y%m%d%H%M"))

def AuViewSql(file_dir):
    with open(file_dir,'r',encoding='utf-8') as f:
        RtData = f.read()
    return RtData

def AUExecOracle(**kwargs):
    # judge_op_type(kwargs['input_sql_type'],kwargs['input_sql'])
    # print('exec',kwargs['input_sql'])
    AuFileDir = kwargs['AuAdFileDir']
    with open(AuFileDir,'r',encoding='utf-8') as f:
        input_sql = f.read()
    db_exec = db_audit_map[kwargs['user']][kwargs['AuAdDbUser']]
    sql_batch = input_sql.rstrip().rstrip(';').split(';')
    db_record = ''
    cont_state = ''
    for bath_exec in sql_batch:
        try:
            db_msg = db_exec.exec_oracle(bath_exec)
        except cx_Oracle.DatabaseError as orcl_error_msg:
            db_msg = str(orcl_error_msg) + ';' + '\n'
            cont_state = '1'
        db_record = db_record + db_msg
    if cont_state == '1':
        db_exec.rollback_oracle()
        db_record = db_record + '数据库执行失败，事务已经全部回滚！！！'
    return db_record

def AuCommitOracle(**kwargs):
    db_exec = db_audit_map[kwargs['user']][kwargs['AuAdDbUser']]
    db_exec.commit_oracle()
    AuditFile = kwargs['AuAdFileDir']
    AudifFileName = AuditFile.split(os.sep)[len(AuditFile.split(os.sep))-1]
    FileRecord = BaseFileD + os.sep + AudifFileName
    if os.path.isdir(BaseFileD):
        pass
    else:
        os.makedirs(BaseFileD)
    if os.path.isfile(FileRecord):
        pass
    else:
        with open(AuditFile,'r',encoding='utf-8') as f:
            with open(FileRecord,'a+',encoding='utf-8') as new_f:
                for line in f:
                    new_f.write(line)
        models.op_oracle_record.objects.create(exec_user=kwargs['user'], req_no=kwargs['AuAdReqNo'],
                                               stamp=time.strftime("%Y%m%d%H%M%S"), file_dir=FileRecord)
        Admodels.db_audit_record.objects.filter(id=kwargs['id']).update(state='S')
    return '审核数据提交完成'


def AURollabckOracle(user,db_user):
    db_exec = db_audit_map[user][db_user]
    db_exec.rollback_oracle()
    return '审核数据回滚完成'