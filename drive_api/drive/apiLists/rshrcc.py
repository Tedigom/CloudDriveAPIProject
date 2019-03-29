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


# 6-1. 파일/폴더 공유취소(resource share cancel, rshrcc)

@api_view(['GET','POST'])
def resource_share_cancel(request):
    if request.method == 'GET':

        # Request Parameter : userID, ResourceKey

        userID = request.GET['userID']  # UserID : 사용 유저 ID
        resourceKey = request.GET['resourceID']  # resourceKey : 공유할 폴더/파일의 리소스

    elif request.method == 'POST':
        userID = request.POST['userID']
        resourceKey = request.POST['resourceID']

    # 검증 작업 : userID, resourceKey가 데이터베이스에 존재하는지 확인

    userCheck = Users.objects.get(userID=userID)
    resourceCheck = Resources.objects.get(userID=userID, resourceID=resourceKey)

    # 검증작업을 통과한 경우에만 코드를 실행
    # with transaction.atomic():
        # transaction start
    if userCheck and resourceCheck:
        methods = Methods()
        shareStatus = resourceCheck.shareStatus
        if shareStatus == 'True':
            shareData = resourceCheck.shareID
            try:
                with transaction.atomic():
                    # transaction start
                    # shareUsers 테이블에서 해당 share번호를 가지고 있는 shareusers를 모두 지움
                    ShareUsers.objects.filter(shareID=shareData.shareID).delete()
                    # share 테이블에서 해당 share 번호를 지움
                    shareData.delete()
                    # resource에 데이터 업데이트
                    resourceCheck.shareStatus = 'False'
                    resourceCheck.shareID = None
                    resourceCheck.save()

            except:
                print("핵심 로직 실패 - roll back")
                return Response(404)

        elif shareStatus == 'False':
            print("이미 sharestatus가 false임")
        else:
            print("shareStatus가 잘못 입력되어있는 경우")

    timestamp = datetime.datetime.now()
    contents = ''
    fullURL = 'http://localhost:8001/logapi/log/?datetime={0}&type=rshrcc&userID={1}&parentDirID=0&contents={3}&resourceID={4}&shareID={2}&shareUsersID=0'.format(
        timestamp, userID, shareData.shareID, contents, resourceKey)
    requestQueue = Background._getInstance()
    requestQueue.put(fullURL)

    resultQuerySet = Resources.objects.filter(userID=userCheck, parentDirID=resourceCheck.parentDirID)
    serializer = DriveSerializer(resultQuerySet, many=True)
    return Response(serializer.data)
