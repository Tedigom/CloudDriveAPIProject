
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drive.viewsMethod import Methods

from drive.serializers import DriveSerializer
from drive.models import Resources, Users, Shares, ShareUsers
from drive.background import Background

import datetime
import requests

from django.db import transaction

# 6. 파일/폴더 공유하기(resource share, rshr)
@api_view(['GET','POST'])
def resource_share(request):
    if request.method == 'GET':

        # Request Parameter : userID, ResourceKey, shareUsersID

        userID = request.GET['userID']  # UserID : 사용 유저 ID
        resourceKey = request.GET['resourceID']  # resourceKey : 공유할 폴더/파일의 리소스 키
        shareUsersID = request.GET['shareUsersID']  # shareUsersID : 공유할 사람들의 ID // 공유할 사람들이 여러명일 경우 ','로 구분한다.

    elif request.method == 'POST':
        userID = request.POST['userID']
        resourceKey = request.POST['resourceID']
        shareUsersID = request.POST['shareUsersID']

    # 검증 작업 : userID, resourceKey, shareUsers 가 데이터베이스에 존재하는지 확인

    userCheck = Users.objects.get(userID=userID)
    resourceCheck = Resources.objects.get(userID=userID, resourceID=resourceKey)
    shareUserList = shareUsersID.split(',')
    for shareUser in shareUserList:
        Users.objects.get(userID=shareUser)

    # with transaction.atomic():
        # Transaction start
        # 검증작업을 통과한 경우에만 코드를 실행
    if userCheck and resourceCheck:
        methods = Methods()
        shareStatus = resourceCheck.shareStatus

        if shareStatus == 'False':
            try:
                with transaction.atomic():
                    # share에 데이터 생성
                    shareData = Shares(resourceID=resourceCheck.resourceID, resourceName=resourceCheck.resourceName,
                                    shareDateTime=datetime.datetime.now())
                    shareData.save()

                    # shareUsers에 데이터 생성
                    for i in range(len(shareUserList)):
                        shareUserCheck = Users.objects.get(userID=shareUserList[i])
                        shareUserData = ShareUsers(shareID=shareData, userID=shareUserCheck)
                        shareUserData.save()

                    # resource에 데이터 업데이트
                    resourceCheck.shareStatus = 'True'
                    resourceCheck.shareID = shareData
                    resourceCheck.save()
            except:
                    print("핵심 로직 실패 - rollback")
                    return Response(status=404)

        elif shareStatus == 'True':
            print("이미 status가 true")
        else:
            print("shareStatus가 잘못 입력되어있는 경우")

    timestamp = datetime.datetime.now()
    contents = ''
    fullURL = 'http://localhost:8001/logapi/log/?datetime={0}&type=rshr&userID={1}&parentDirID=0&contents={3}&resourceID={4}&shareID={2}&shareUsersID={5}'.format(
        timestamp, userID, shareData.shareID, contents, resourceKey, shareUsersID)
    requestQueue = Background._getInstance()
    requestQueue.put(fullURL)

    resultQuerySet = Resources.objects.filter(userID=userCheck, parentDirID=resourceCheck.parentDirID)
    serializer = DriveSerializer(resultQuerySet, many=True)
    return Response(serializer.data)
