from typing import List

from django.db import models

# Create your models here.
from django.db import models


class Users(models.Model):
    userID = models.CharField(max_length = 50, primary_key= True)     # PK
    userName = models.CharField(max_length = 50)
    userEmail = models.CharField(max_length = 50)

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

    def __str__(self):
        return self.resourceName


class Shares(models.Model):
    shareID = models.AutoField(primary_key= True)    # PK
    resourceID = models.CharField(max_length = 50)
    resourceName = models.CharField(max_length= 50)
    shareDateTime = models.DateTimeField()

    def __str__(self):
        return self.shareID


class ShareUsers(models.Model):
    shareUsersKey = models.AutoField(primary_key = True) # PK
    shareID = models.ForeignKey(Shares, on_delete=models.CASCADE, db_column='shareID', null= False)  # FK
    userID = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='userID', null = False) # FK
    authority = models.CharField(max_length = 50, blank=True, null=True)

    def __str__(self):
        return self.shareUsersKey

class FailedLog(models.Model):
    failedLogID = models.AutoField(primary_key= True) # PK
    failedLogContents = models.TextField()

    def __str__(self):
        return self.failedLogID

