from django.shortcuts import render,redirect,HttpResponse
from bk_manage import models
from db_code.DbexecMethod import audit_commit,AuViewSql,AUExecOracle,AURollabckOracle,AuCommitOracle,ViewAuditText,ViewAuditResult,AU_NoPass_record
from dbaudit import models as Admodels
from db_code.op_db_file_module import db_audit_map,Oracle_op
import json,time

# Create your views here.

# def audit_login(request):
#     # url_dir = request.path_info
#     if request.session.get('AuditUsername', None) == None:
#         error_msg = ""
#         if request.method == "GET":
#             return render(request, 'audit_user_login.html', {'error_msg': error_msg})
#         elif request.method == "POST":
#             user = request.POST.get('username', None)
#             passwd = request.POST.get('password', None)
#             if models.userinfo.objects.filter(username=user, password=passwd).count() == 0:
#                 error_msg = "用户名或密码错误"
#                 return render(request, 'audit_user_login.html', {'error_msg': error_msg})
#             else:
#                 response = redirect('/dbaudit/auditview')
#                 request.session['AuditUsername'] = user
#                 request.session['QueryRecordDate'] = time.strftime("%Y%m%d")
#                 request.session.set_expiry(0)
#                 return response
#     else:
#         return redirect('/dbaudit/auditview')

# def audit_view(request):
#     user = request.session.get('AuditUsername', None)
#     if user != None:
#         if request.method == "GET":
#             db_user = models.userinfo.objects.filter(username='all').get().user_priv.split(',')
#             CommitDate = request.session.get('QueryRecordDate', None)
#             if user == 'op':
#                 AuComRecord = Admodels.db_audit_record.objects.filter(CommitDate=CommitDate).all()
#                 return render(request, 'audit_view.html',
#                               {'current_user': user, 'db_user': db_user, 'AuComRecord': AuComRecord})
#             else:
#                 AuComRecord = Admodels.db_audit_record.objects.filter(exec_user=user).filter(CommitDate=CommitDate).all()
#                 return render(request, 'audit_view.html',{'current_user': user,'db_user':db_user,'AuComRecord':AuComRecord})
#         if request.method == 'POST':
#             pass
#     else:
#         return redirect('/dbaudit/login')

def commit_audit(request):
    user = request.session.get('username', None)
    if user != None:
        if request.method == "GET":
            db_user = models.userinfo.objects.filter(username='all').get().user_priv.split(',')
            return render(request, 'audit_view.html',{'current_user': user,'db_user':db_user})
        if request.method == "POST":
            select_user = request.POST.get('select_user',None)
            audit_req = request.POST.get('audit_req', None)
            audit_sql = request.POST.get('audit_sql', None)
            query_desc = request.POST.get('query_desc',None)
            audit_commit(select_user=select_user,audit_req=audit_req,audit_sql=audit_sql,query_desc=query_desc,exec_user=user)
            return HttpResponse('提交完成')
    else:
        return redirect('/dbop/login')

def User_Viewtext(request):
    user = request.session.get('username', None)
    if user != None:
        if request.method == "POST":
            id = request.POST.get('msg_id',None)
            AuditFileName = Admodels.db_audit_record.objects.filter(id=id).get().file_dir
            AuditRecordText = ViewAuditText(AuditFileName)
            AuditRecordText = AuditRecordText.split(';')
            return HttpResponse(json.dumps(AuditRecordText))
    else:
        return redirect('/dbop/login')
def User_ViewResult(request):
    user = request.session.get('username', None)
    if user != None:
        if request.method == "POST":
            id = request.POST.get('msg_id', None)
            AuditResultFileName = Admodels.db_audit_record.objects.filter(id=id).get().exec_result
            if AuditResultFileName == '':
                return HttpResponse(json.dumps(('提交记录待审核').split(';')))
            else:
                AuditResultText = ViewAuditResult(AuditResultFileName)
                AuditResultText = AuditResultText.split(';')
                return HttpResponse(json.dumps(AuditResultText))
    else:
        return redirect('/dbop/login')

def AuditUser_login(request):
    if request.session.get('DbAuditUsername', None) == None:
        error_msg = ""
        if request.method == "GET":
            return render(request, 'DbAudit_user_login.html', {'error_msg': error_msg})
        elif request.method == "POST":
            user = request.POST.get('username', None)
            passwd = request.POST.get('password', None)
            if Admodels.aduit_userinfo.objects.filter(username=user, password=passwd).count() == 0:
                error_msg = "用户名或密码错误"
                return render(request, 'DbAudit_user_login.html', {'error_msg': error_msg})
            else:
                response = redirect('/dbaudit/dbauditview')
                userpri = Admodels.aduit_userinfo.objects.filter(username=user).get().audit_priv.split(',')
                privdir = {}
                for i in userpri:
                    privdir[i] = Oracle_op(i, models.oracle_db_user_info.objects.filter(
                        username=i).get().password)
                db_audit_map[user] = privdir
                request.session['DbAuditUsername'] = user
                request.session.set_expiry(0)
                return response
    else:
        return redirect('/dbaudit/dbauditview')

def AuditUser_view(request):
    user = request.session.get('DbAuditUsername', None)
    if user != None:
        if request.method == "GET":
            Admsg = Admodels.db_audit_record.objects.filter(state='W').all()
            return render(request, 'DbAudit_view.html', {'current_user': user,'Admsg':Admsg})
        if request.method == 'POST':
            pass
    else:
        return redirect('/dbaudit/AUlogin')

def AUview_sql(request):
    user = request.session.get('DbAuditUsername', None)
    if user != None:
        if request.method == "GET":
            return redirect('/dbaudit/dbauditview')
        elif request.method == "POST":
            msg_id = request.POST.get('msg_id',None)
            file_dir = Admodels.db_audit_record.objects.filter(id=msg_id).get().file_dir
            SqlText = AuViewSql(file_dir)
            SqlText = SqlText.split(';')
            return HttpResponse(json.dumps(SqlText))
    else:
        return redirect('/dbaudit/AUlogin')

def AUAudit_Pass(request):
    user = request.session.get('DbAuditUsername', None)
    if user != None:
        if request.method == "GET":
            return redirect('/dbaudit/dbauditview')
        elif request.method == "POST":
            msg_id = request.POST.get('msg_id', None)
            SelResult = Admodels.db_audit_record.objects.filter(id=msg_id).all()
            AuAdFileDir = SelResult.get().file_dir
            AuAdDbUser = SelResult.get().db_user
            db_record = AUExecOracle(AuAdFileDir=AuAdFileDir,user=user,AuAdDbUser=AuAdDbUser,id=msg_id)
            db_record = db_record.split(';')
            return HttpResponse(json.dumps(db_record))

    else:
        return redirect('/dbaudit/AUlogin')

def AUAudit_Nopass(request):
    user = request.session.get('DbAuditUsername', None)
    if user != None:
        if request.method == "GET":
            return redirect('/dbaudit/dbauditview')
        elif request.method == "POST":
            msg_id = request.POST.get('msg_id', None)
            AuAdFileDir = Admodels.db_audit_record.objects.filter(id=msg_id).get().file_dir
            AU_NoPass_record(AuAdFileDir,msg_id)
            return HttpResponse('审核提交完成')
    else:
        return redirect('/dbaudit/AUlogin')

def AUAudit_commit(request):
    user = request.session.get('DbAuditUsername', None)
    if user != None:
        if request.method == "GET":
            return redirect('/dbaudit/dbauditview')
        elif request.method == "POST":
            msg_id = request.POST.get('msg_id', None)
            SelResult = Admodels.db_audit_record.objects.filter(id=msg_id).all()
            AuAdFileDir = SelResult.get().file_dir
            AuAdDbUser = SelResult.get().db_user
            AuAdReqNo = SelResult.get().req_no
            AuAdExecResultF = SelResult.get().exec_result
            ret_data = AuCommitOracle(AuAdFileDir=AuAdFileDir,AuAdDbUser=AuAdDbUser,AuAdReqNo=AuAdReqNo,user=user,id=msg_id,AuAdExecResultF=AuAdExecResultF)
            return HttpResponse(ret_data)
    else:
        return redirect('/dbaudit/AUlogin')

def AUAudit_rollback(request):
    user = request.session.get('DbAuditUsername', None)
    if user != None:
        if request.method == "GET":
            return redirect('/dbaudit/dbauditview')
        elif request.method == "POST":
            msg_id = request.POST.get('msg_id', None)
            db_user = Admodels.db_audit_record.objects.filter(id=msg_id).get().db_user
            AuAdExecResultF = Admodels.db_audit_record.objects.filter(id=msg_id).get().exec_result
            ret_data = AURollabckOracle(user,db_user,AuAdExecResultF)
            return HttpResponse(ret_data)
    else:
        return redirect('/dbaudit/AUlogin')

def Query_RecordDate(request):
    user = request.session.get('username', None)
    if user != None:
        if request.method == "POST":
            QueryDate = request.POST.get('QueryDate',None)
            request.session['QueryRecordDate'] = QueryDate
            return HttpResponse('')
    else:
        return redirect('/dbop/login')