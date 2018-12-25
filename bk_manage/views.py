from django.shortcuts import render

# Create your views here.

from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from . import models
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

def user_info(request):
    admin_user = request.COOKIES.get('adminusername')
    if admin_user != None:
        url_dir = request.path_info
        all_userinfo = models.userinfo.objects.all()
        error_msg = ""
        if request.method == "GET":
            return render(request,'bkmanage_view.html',{'all_userinfo':all_userinfo,'error_msg':error_msg})
        elif request.method == "POST":
            if request.POST.get('username',None) == '' or request.POST.get('password',None) =='' or request.POST.get('priv',None) == '':
                error_msg = "用户信息不完整"
                return render(request, 'bkmanage_view.html', { 'all_userinfo': all_userinfo,'error_msg':error_msg})
            else:
                models.userinfo.objects.create(username=request.POST.get('username',None),password=request.POST.get('password',None),user_priv=request.POST.get('priv',None))
                all_userinfo = models.userinfo.objects.all()
                return render(request, 'bkmanage_view.html',{ 'all_userinfo': all_userinfo, 'error_msg': error_msg})
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