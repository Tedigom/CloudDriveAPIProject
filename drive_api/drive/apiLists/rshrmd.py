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


# 6-2. 파일/폴더 공유 share user 삭제 (resource share member delete, rshrmd)

@api_view(['GET','POST'])
def resource_share_member_delete(request):
    if request.method == 'GET':

        # Request Parameter : userID, ResourceKey

        userID = request.GET['userID']  # UserID : 사용 유저 ID
        resourceKey = request.GET['resourceID']  # resourceKey : 공유할 폴더/파일의 리소스
        shareUsersID = request.GET['shareUsersID']  # shareUsersID : 추가로 공유할 사람들의 ID // 공유할 사람들이 여러명일 경우 ','로 구분한다.

    elif request.method == 'POST':
        userID = request.POST['userID']
        resourceKey = request.POST['resourceID']
        shareUsersID = request.POST['shareUsersID']

    # 검증 작업 : userID, resourceKey가 데이터베이스에 존재하는지 확인

    userCheck = Users.objects.get(userID=userID)
    resourceCheck = Resources.objects.get(userID=userID, resourceID=resourceKey)
    shareUserList = shareUsersID.split(',')
    for shareUser in shareUserList:
        Users.objects.get(userID=shareUser)

    # with transaction.atomic():
        # transaction start
    # 검증작업을 통과한 경우에만 코드를 실행
    if userCheck and resourceCheck:
        methods = Methods()
        if resourceCheck.shareStatus == 'True':
            shareData = Shares.objects.get(shareID=resourceCheck.shareID.shareID)
            for i in range(len(shareUserList)):
                shareUserCheck = Users.objects.get(userID=shareUserList[i])
                if ShareUsers.objects.filter(shareID=shareData, userID=shareUserCheck).exists():
                    try:
                        with transaction.atomic():
                            shareUserData = ShareUsers.objects.filter(shareID=shareData, userID=shareUserCheck)
                            shareUserData.delete()
                    except:
                        print("핵심로직 실패 - roll back")
                        return Response(status=404)
                else:
                    print("공유되지 않은 사용자")
        else:
            print("실행할 수 없음")

    shareData.save()
    timestamp = datetime.datetime.now()
    contents = ''
    fullURL = 'http://localhost:8001/logapi/log/?datetime={0}&type=rshrmd&userID={1}&parentDirID=0&contents={3}&resourceID={4}&shareID={2}&shareUsersID={5}'.format(
        timestamp, userID, shareData.shareID, contents, resourceKey, shareUsersID)
    requestQueue = Background._getInstance()
    requestQueue.put(fullURL)

    resultQuerySet = Resources.objects.filter(userID=userCheck, parentDirID=resourceCheck.parentDirID)
    serializer = DriveSerializer(resultQuerySet, many=True)
    return Response(serializer.data)