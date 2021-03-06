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

#T_PUB_RSTS csdacm,csdact，gsdpay 四组

def judge_op_type(input_sql_type, input_sql):
    judge_stat = 0
    if input_sql_type.lower() == 'noeaa' :
        spl_sql = input_sql.rstrip().rstrip(';').split(';')
        for i in NotAllowExec:
            for j in spl_sql:
                matchResult = re.match('^\s*%s'%i,j,flags=re.IGNORECASE)
                if matchResult != None:
                    judge_stat = 1
        return judge_stat
    elif input_sql_type.lower() == 'all' :
        return 0

def judge_dml_ddl(input_sql):
    dml_true = 0
    ddl_true = 0
    input_sql = re.sub('--.*\n', '', input_sql)
    input_sql = re.sub('\n', ' ', input_sql)
    for i in ALLTYPE:
        input_sql = re.sub(';\s*%s'%i,'\n%s'%i,input_sql,flags=re.IGNORECASE)
    input_sql = input_sql.rstrip().rstrip(';').splitlines()
    for sql_type in DML:
        for j in input_sql:
            if re.match('^\s*%s'%sql_type,j,flags=re.IGNORECASE) != None:
                dml_true = 1
    for sql_type in DDL:
        for j in input_sql:
            if re.match('^\s*%s'%sql_type,j,flags=re.IGNORECASE) != None:
                ddl_true = 1
    if dml_true == 1 and ddl_true != 1:
        return 'dml'
    elif dml_true != 1 and ddl_true == 1:
        return 'ddl'
    else:
        return 'all'

def dml_sql_transform(input_sql):
    input_sql = re.sub('\n\t*','\n',input_sql)
    input_sql = re.sub('\n *','\n',input_sql)
    input_sql = re.sub('\n', '\t ', input_sql)
    for i in DML:
        input_sql = re.sub(';\s*%s'%i,'\n%s'%i,input_sql,flags=re.IGNORECASE)
    input_sql = re.sub('--','\n--',input_sql)
    for j in DML:
        input_sql = re.sub('\t %s'%j,'\t \n%s'%j,input_sql,flags=re.IGNORECASE)
    input_sql = input_sql.lstrip().rstrip().rstrip(';').splitlines()
    return input_sql

def execute_oracle_file(**kwargs):
    exec_status = judge_op_type(kwargs['input_sql_type'],kwargs['input_sql'])
    if exec_status == 1:
        return '输入的数据库操作语言有误，请检查输入的sql。'
    elif exec_status == 0:
        # print('exec',kwargs['input_sql'])
        #sql_batch = kwargs['input_sql'].rstrip().rstrip(';').split(';')
        sql_batch = dml_sql_transform(kwargs['input_sql'])
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
    filebasedir = BaseFileD + os.sep + time.strftime("%Y%m%d")
    if os.path.isdir(filebasedir):
        pass
    else:
        os.makedirs(filebasedir)
    file_dir = filebasedir + os.sep + file_name
    tmp_dir = kwargs['tmpfilename']
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
    tmp_dir = kwargs['tmpfilename']
    tmp_file_clean(tmp_dir)


def audit_commit(**kwargs):
    # 写入auditfile中，写入mysql数据库审计表中(提交用户，需求号，sql文件路径，审核状态位,问题描述)
    auditfile = '%s_%s_%s.sql'%(kwargs['exec_user'],kwargs['audit_req'],time.strftime("%Y%m%d%H%M%S"))
    auditfiledir = BaseAuditFileD + os.sep + time.strftime("%Y%m%d")
    auditfiledpath = auditfiledir + os.sep + auditfile
    if os.path.isdir(auditfiledir):
        pass
    else:
        os.makedirs(auditfiledir)
    with open(auditfiledpath,'a+',encoding='utf-8') as f:
        #f.write('--%s \n'%kwargs['query_desc'])
        f.write(kwargs['audit_sql'])
    Admodels.db_audit_record.objects.create(exec_user=kwargs['exec_user'],db_user=kwargs['select_user'],req_no=kwargs['audit_req'],
                                            state='W',file_dir=auditfiledpath,DescMessage=kwargs['query_desc'],CommitDate=time.strftime("%Y%m%d"),stamp=time.strftime("%Y%m%d%H%M"))

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
    judge_reslut = judge_dml_ddl(input_sql)
    if judge_reslut == 'all':
        db_record = '请将sql语句根据不同类型分别提交！;' + '\n'
        # 执行结果写入文件和数据库中
        AuditResultfFileName = AuFileDir.split(os.sep)[len(AuFileDir.split(os.sep)) - 1]
        AuditResultfFDir = BaseAuditRecordFileD + os.sep + time.strftime("%Y%m%d")
        if os.path.isdir(AuditResultfFDir):
            pass
        else:
            os.makedirs(AuditResultfFDir)
        AuditResultfFile = AuditResultfFDir + os.sep + AuditResultfFileName
        Audit_Record_write(AuditResultfFile, db_record)
        Admodels.db_audit_record.objects.filter(id=kwargs['id']).update(exec_result=AuditResultfFile)
        return db_record
    elif judge_reslut == 'dml':
        sql_batch = dml_sql_transform(input_sql)
        #sql_batch = input_sql.rstrip().rstrip(';').split(';')
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
            db_record = db_record + '数据库执行失败，事务已经全部回滚！！！' + ';' + '\n'
        #执行结果写入文件和数据库中
        AuditResultfFileName = AuFileDir.split(os.sep)[len(AuFileDir.split(os.sep))-1]
        AuditResultfFDir = BaseAuditRecordFileD + os.sep + time.strftime("%Y%m%d")
        if os.path.isdir(AuditResultfFDir):
            pass
        else:
            os.makedirs(AuditResultfFDir)
        AuditResultfFile = AuditResultfFDir + os.sep + AuditResultfFileName
        Audit_Record_write(AuditResultfFile, db_record)
        Admodels.db_audit_record.objects.filter(id=kwargs['id']).update(exec_result=AuditResultfFile)
        return db_record
    elif judge_reslut == 'ddl':
        #sql_batch = dml_sql_transform(input_sql)
        input_sql = re.sub('--.*\n', '', input_sql)
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
        #执行结果写入文件和数据库中
        AuditResultfFileName = AuFileDir.split(os.sep)[len(AuFileDir.split(os.sep))-1]
        AuditResultfFDir = BaseAuditRecordFileD + os.sep + time.strftime("%Y%m%d")
        if os.path.isdir(AuditResultfFDir):
            pass
        else:
            os.makedirs(AuditResultfFDir)
        AuditResultfFile = AuditResultfFDir + os.sep + AuditResultfFileName
        Audit_Record_write(AuditResultfFile, db_record)
        Admodels.db_audit_record.objects.filter(id=kwargs['id']).update(exec_result=AuditResultfFile)
        return db_record

def AuCommitOracle(**kwargs):
    db_exec = db_audit_map[kwargs['user']][kwargs['AuAdDbUser']]
    db_exec.commit_oracle()
    AuditFile = kwargs['AuAdFileDir']
    AudifFileName = AuditFile.split(os.sep)[len(AuditFile.split(os.sep))-1]
    AudFileRecDir = BaseFileD + os.sep + time.strftime("%Y%m%d")
    FileRecord = AudFileRecDir + os.sep + AudifFileName
    if os.path.isdir(AudFileRecDir):
        pass
    else:
        os.makedirs(AudFileRecDir)
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
        AuAdExecResultF = kwargs['AuAdExecResultF']
        with open(AuAdExecResultF,'a+',encoding="utf-8") as Rf:
            Rf.write('提交;'+ '\n')
    return '审核数据提交完成'


def AURollabckOracle(user,db_user,AuAdExecResultF):
    db_exec = db_audit_map[user][db_user]
    db_exec.rollback_oracle()
    with open(AuAdExecResultF, 'a+', encoding="utf-8") as f:
        f.write('回滚;' + '\n')
    return '审核数据回滚完成'

def ViewAuditText(ViewTextName):
    with open(ViewTextName,'r',encoding="utf-8") as f:
        ATRtDate = f.read()
    return ATRtDate

def ViewAuditResult(AuditResultFileName):
    with open(AuditResultFileName,'r',encoding="utf-8") as f:
        ARRtDate = f.read()
    return ARRtDate

def AU_NoPass_record(AuAdFileDir,msg_id):
    AuditResultfFileName = AuAdFileDir.split(os.sep)[len(AuAdFileDir.split(os.sep)) - 1]
    AuditResultfFDir = BaseAuditRecordFileD + os.sep + time.strftime("%Y%m%d")
    if os.path.isdir(AuditResultfFDir):
        pass
    else:
        os.makedirs(AuditResultfFDir)
    AuditResultfFile = AuditResultfFDir + os.sep + AuditResultfFileName
    Audit_Record_write(AuditResultfFile, '审批不通过，请检查提交的SQL')
    Admodels.db_audit_record.objects.filter(id=msg_id).update(exec_result=AuditResultfFile)
    Admodels.db_audit_record.objects.filter(id=msg_id).update(state='F')