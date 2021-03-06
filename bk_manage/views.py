from django.shortcuts import render

# Create your views here.

from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from . import models
from dbaudit import models as Aumodels
import os

def login(request):
    url_dir = request.path_info
    error_msg = ""
    if request.method == "GET":
        return render(request, 'bkmanage_login.html',{'error_msg':error_msg})
    elif request.method == "POST":
        user = request.POST.get('username',None)
        passwd = request.POST.get('password',None)
        if models.user_admin.objects.filter(username=user,password=passwd).count() == 0:
            error_msg = "用户名或密码错误"
            return render(request, 'bkmanage_login.html',{'error_msg':error_msg})
        else:
            response = redirect('/bkmanage/userinfo')
            response.set_cookie('adminusername',user)
            return  response

def logout(request):
    request.session.clear()
    return redirect('/bkmanage/login')


def user_info(request):
    admin_user = request.COOKIES.get('adminusername')
    if admin_user != None:
        url_dir = request.path_info
        all_userinfo = models.userinfo.objects.all()
        audit_userinfo = Aumodels.aduit_userinfo.objects.all()
        db_info = models.oracle_db_info.objects.all()
        db_user_info = models.oracle_db_user_info.objects.all()
        error_msg = ""
        if request.method == "GET":
            return render(request,'bkmanage_view.html',{'all_userinfo':all_userinfo,'error_msg':error_msg,'audit_userinfo':audit_userinfo,'db_info':db_info,'db_user_info':db_user_info})
        elif request.method == "POST":
            username = request.POST.get('username',None)
            password = request.POST.get('password',None)
            priv = request.POST.get('priv',None)
            if username == '' or password == '' or priv == '':
                return HttpResponse('用户信息不完整')
            else:
                models.userinfo.objects.create(username=username,password=password,user_priv=priv)
                return HttpResponse('添加完成')
    else:
        return redirect('/bkmanage/login')

def BmUser_Del(request):
    admin_user = request.COOKIES.get('adminusername')
    if admin_user != None:
        if request.method == "POST":
            userid = request.POST.get('userid',None)
            models.userinfo.objects.filter(userid=userid).delete()
            return HttpResponse('')
    else:
        return redirect('/bkmanage/login')

def AuditUser_add(request):
    admin_user = request.COOKIES.get('adminusername')
    if admin_user != None:
        if request.method == "POST":
            Auditusername = request.POST.get('username',None)
            Auditpassword = request.POST.get('password',None)
            if Auditusername == '' or Auditpassword == '' :
                return HttpResponse('用户信息不完整')
            else:
                Auditpriv = models.userinfo.objects.filter(username='all').get().user_priv
                Aumodels.aduit_userinfo.objects.create(username=Auditusername,password=Auditpassword,audit_priv=Auditpriv)
                return HttpResponse('审计用户添加完成')
    else:
        return redirect('/bkmanage/login')