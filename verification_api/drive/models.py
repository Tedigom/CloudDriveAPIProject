from typing import List


# Create your models here.
from django.db import models


class Users(models.Model):
    userID = models.CharField(max_length = 50, primary_key= True)     # PK
    userName = models.CharField(max_length = 50)
    userEmail = models.CharField(max_length = 50)

    class META:
        app_label = 'drive'
    def __str__(self):
        return self.userID

# 파일과 폴더 모두 합친 형태의 Resource table
class Resources(models.Model):

    resourceID = models.AutoField(primary_key= True)     # PK
    userID = models.ForeignKey(Users, on_delete= models.CASCADE, db_column='userID')     # FK
    resourceName = models.CharField(max_length = 50)
    parentDirID = models.CharField(max_length = 50)    # FK
    fullPath = models.CharField(max_length = 500)
    fileSize = models.IntegerField()
    fileType = models.CharField(max_length = 50, choices=(('File', 'File'),('Directory','Directory'),))       # File / Directory 구분
    childCount = models.IntegerField(default=0)     # 해당 Resource의 자식 수

    shareStatus = models.CharField(max_length=50)    # 공유 여부 ( True / False )
    shareID = models.ForeignKey('Shares', blank = True, null= True, on_delete=models.SET_NULL, db_column = 'shareID', default = None)# FK

    class META:
        app_label = 'drive'
    def __str__(self):
        return self.resourceName+' '+self.parentDirID+' '+self.fullPath


class Shares(models.Model):
    shareID = models.AutoField(primary_key= True)    # PK
    resourceID = models.CharField(max_length = 50)
    resourceName = models.CharField(max_length= 50)
    shareDateTime = models.DateTimeField()
    revision = models.IntegerField(default=0)  # 수정 여부 (create, update 시 revision이 1이 됨 // 검증 통과 시 revision은 0이 됨)

    class META:
        app_label = 'drive'
    def __str__(self):
        return self.shareID


class ShareUsers(models.Model):
    shareUsersKey = models.AutoField(primary_key = True) # PK
    shareID = models.ForeignKey(Shares, on_delete=models.CASCADE, db_column='shareID', null= False)  # FK
    userID = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='userID', null = False) # FK
    authority = models.CharField(max_length = 50, blank=True, null=True)
    revision = models.IntegerField(default=0)  # 수정 여부 (create, update 시 revision이 1이 됨 // 검증 통과 시 revision은 0이 됨)

    class META:
        app_label = 'drive'
    def __str__(self):
        return self.shareUsersKey

class FailedLog(models.Model):
    failedLogID = models.AutoField(primary_key= True) # PK
    failedLogContents = models.TextField()

    class META:
        app_label = 'drive'
    def __str__(self):
        return self.failedLogID


class Log(models.Model):
    logID = models.AutoField(primary_key= True) #PK
    logDateTime = models.DateTimeField()
    logType = models.CharField(max_length=50, blank= False, null= False)
    logUserID = models.CharField(max_length=50, blank = False, null = False)
    logResourceID = models.IntegerField(blank = True, null = True)
    logParentDirID = models.IntegerField(blank= True, null = True)
    logShareID = models.IntegerField(blank=True, null= True)
    logShareUsersID = models.CharField(max_length=500,blank=True, null= True)
    logContents = models.TextField(blank = True, null=True)
    class META:
        app_label = 'drivelog'

    def __str__(self):
        return self.logContents

class Error(models.Model):
    errorID = models.AutoField(primary_key=True) # PK
    errorQuery = models.TextField(blank = False, null = False)
    errorDateTime = models.DateTimeField()

    def __str__(self):
        return self.errorQuery