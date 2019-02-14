from django.db import models

# Create your models here.

class db_audit_record(models.Model):
    exec_user = models.CharField(max_length=20)
    db_user = models.CharField(max_length=10)
    req_no = models.CharField(max_length=10)
    file_dir = models.CharField(max_length=100)
    state = models.CharField(max_length=1)
    DescMessage = models.CharField(max_length=130)
    stamp = models.CharField(max_length=12)
    exec_result = models.CharField(max_length=100)

class aduit_userinfo(models.Model):
    username = models.CharField(max_length=20,primary_key=True)
    password = models.CharField(max_length=20)
    audit_priv = models.CharField(max_length=200)