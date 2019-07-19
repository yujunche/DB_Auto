"""DB_Auto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
####zzz
from django.conf.urls import url,include

from dbaudit import views
urlpatterns = [
    #url(r'^login' ,views.audit_login),
    #url(r'^auditview',views.audit_view),
    url(r'^commitaudit',views.commit_audit),
    url(r'^UserViewtext',views.User_Viewtext),
    url(r'^UserViewResult',views.User_ViewResult),
    url(r'^AUlogin',views.AuditUser_login),
    url(r'^dbauditview',views.AuditUser_view),
    url(r'^AUViewSql',views.AUview_sql),
    url(r'^AUAdPass',views.AUAudit_Pass),
    url(r'^AUAdNopass',views.AUAudit_Nopass),
    url(r'^AUAdCommit',views.AUAudit_commit),
    url(r'^AUAdRollback',views.AUAudit_rollback),
    url(r'^QueryRecordDate',views.Query_RecordDate),
]
