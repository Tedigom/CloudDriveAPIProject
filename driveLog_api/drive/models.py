from django.db import models

# Create your models here.
from django.db import models

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
    def __str__(self):
        return self.logDateTime

class Error(models.Model):
    errorID = models.AutoField(primary_key=True) # PK
    errorQuery = models.TextField(blank = False, null = False)
    errorDateTime = models.DateTimeField()

    def __str__(self):
        return self.errorQuery