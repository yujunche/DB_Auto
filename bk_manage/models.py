from django.db import models

# Create your models here.

#用户名作为主键
class userinfo(models.Model):
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    user_priv = models.CharField(max_length=200)

class user_admin(models.Model):
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=20)

class oracle_db_info(models.Model):
    env_ip = models.CharField(max_length=20)
    env_port = models.CharField(max_length=5)
    env_sid = models.CharField(max_length=10)
    env_info = models.CharField(max_length=5)

class oracle_db_user_info(models.Model):
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=20)


class op_oracle_record(models.Model):
    exec_user = models.CharField(max_length=20)
    req_no = models.CharField(max_length=20)
    stamp = models.CharField(max_length=20)
    file_dir = models.CharField(max_length=100)