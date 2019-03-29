from rest_framework import serializers
from .models import Log

class DriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('logID','logDateTime','logType','logParentDirID','logResourceID','logShareID','logShareUsersID','logUserID','logContents')