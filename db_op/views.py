from django.shortcuts import render

# Create your views here.
from bk_manage import models
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from db_code import op_db_file_module
from db_code import DbexecMethod
import pickle
# from django.views.decorators.csrf import csrf_exempt,csrf_protect
import json


# from db_code import user_exec

####同一登录用户，事务会冲突   db_connect事务，根据全局字典中通过session中用户名和priv区分，增加随机字符串区分同一登录用户，或者不通过对象实现，对象无法存入session

def user_login(request):
    # url_dir = request.path_info
    if request.session.get('username', None) == None:
        error_msg = ""
        if request.method == "GET":
            return render(request, 'user_login.html', {'error_msg': error_msg})
        elif request.method == "POST":
            user = request.POST.get('username', None)
            passwd = request.POST.get('password', None)
            if models.userinfo.objects.filter(username=user, password=passwd).count() == 0:
                error_msg = "用户名或密码错误"
                return render(request, 'user_login.html', {'error_msg': error_msg})
            else:
                response = redirect('/dbop/userview')
                userpri = models.userinfo.objects.filter(username=user).get().user_priv.split(',')
                privdir = {}
                for i in userpri:
                    privdir[i] = op_db_file_module.Oracle_op(i, models.oracle_db_user_info.objects.filter(
                        username=i).get().password)
                op_db_file_module.db_exec_map[user] = privdir
                request.session['username'] = user
                tmpfilename = DbexecMethod.generate_random_str(16)
                request.session['tmpfilename'] = tmpfilename
                op_db_file_module.tmp_file_create(tmpfilename)
                request.session.set_expiry(0)
                return response
    else:
        return redirect('/dbop/userview')


def user_view(request):
    # url_dir = request.path
    # user = request.COOKIES.get('username')
    user = request.session.get('username', None)
    if user != None:
        if request.method == "GET":
            priv = models.userinfo.objects.filter(username=user).get().user_priv.split(',')
            return render(request, 'user_view.html', {'user_priv': priv, 'current_user': user, })
        if request.method == 'POST':
            pass
    else:
        return redirect('/dbop/login')


def user_logout(request):
    request.session.clear()
    return redirect('/')


def user_exec(request):
    user = request.session.get('username', None)
    if user != None:
        if request.method == 'POST':
            priv = models.userinfo.objects.filter(username=user).get().user_priv.split(',')
            sel_priv = request.POST.get('sel_priv',None)
            input_sql = request.POST.get('input_sql',None)
            #print('view',input_sql)
            tmpfilename = request.session.get('tmpfilename', None)
            db_record = DbexecMethod.execute_oracle_file(input_sql=input_sql,user=user,sel_priv=sel_priv,tmpfilename=tmpfilename)
            # return render(request, 'user_view.html', {'user_priv': priv, 'sel_priv': sel_priv, 'input_sql': input_sql,
            #                                           'db_record': db_record.split(';'), 'current_user': user})
            db_record = db_record.split(';')
            return HttpResponse(json.dumps(db_record))
        else:
            return redirect('/dbop/userview')
    else:
        return redirect('/dbop/login')


def user_commit(request):
    user = request.session.get('username', None)
    sel_priv = request.POST.get('sel_priv')
    tmpfilename = request.session.get('tmpfilename', None)
    req_no = request.POST.get('req_no',None)
    if user != None:
        if request.method == 'POST':
            if req_no == '':
                req_no = 'test'
                #print(req_no)
            DbexecMethod.commit_oracle_file(user=user, sel_priv=sel_priv, tmpfilename=tmpfilename, req_no=req_no)
            return HttpResponse('提交完成')
        else:
            return redirect('/dbop/userview')
    else:
        return redirect('/dbop/login')


def user_rollback(request):
    user = request.session.get('username', None)
    sel_priv = request.POST.get('sel_priv')
    tmpfilename = request.session.get('tmpfilename', None)
    if user != None:
        if request.method == 'POST':
            DbexecMethod.rollback_oracle_file(user=user, sel_priv=sel_priv, tmpfilename=tmpfilename)
            return HttpResponse('回滚完成')
        else:
            return redirect('/dbop/userview')
    else:
        return redirect('/dbop/login')
