from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response

from drive.serializers import DriveSerializer
from drive.models import Log, Error

@api_view(['GET','POST'])   # HTTP Method : GET, POST
def getLog(request):
    if request.method == 'GET':
        datetime = request.GET['datetime'] # log datetime
        type = request.GET['type'] # log type
        userID = request.GET['userID'] # log userID
        resourceID = request.GET['resourceID'] # log resourceID
        parentDirID = request.GET['parentDirID'] # log parentDirID
        shareID = request.GET['shareID'] # log shareID
        shareUsersID = request.GET['shareUsersID'] # log shareUsersID
        contents = request.GET['contents']      # log contents

    elif request.method == 'POST':
        datetime = request.POST['datetime']
        type = request.POST['type']
        userID = request.POST['userID']
        resourceID = request.POST['resourceID']
        parentDirID = request.POST['parentDirID']
        shareID = request.POST['shareID']
        shareUsersID = request.POST['shareUsersID']
        contents = request.POST['contents']

    newLog = Log(logDateTime = datetime, logType= type, logUserID=userID,logResourceID=resourceID,
                 logParentDirID=parentDirID, logShareID = shareID, logShareUsersID = shareUsersID  ,logContents=contents)
    newLog.save()

    queryset = Log.objects.all()
    serializer = DriveSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])   # HTTP Method : GET
def getError(request):
    query = request.GET['query']
    timestamp = request.GET['timestamp']

    newError = Error(errorQuery=query,errorDateTime=timestamp)
    newError.save()

    queryset = Error.objects.all()
    serializer = DriveSerializer(query, many=True)
    return Response(serializer.data)


