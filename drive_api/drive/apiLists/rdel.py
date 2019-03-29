
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from drive.serializers import DriveSerializer
from drive.models import Resources, Users, Shares, ShareUsers
from drive.viewsMethod import Methods
from drive.background import Background

import datetime
import requests

from django.db import transaction, connection

# 4. 파일/폴더 삭제(resource delete, rdel)
@api_view(['GET','POST'])
def resource_delete(request):

    if request.method == 'GET':

        # Request Parameter : userID, ResourceKey

        userID = request.GET['userID']  # UserID : 사용 유저 ID
        resourceKey = request.GET['resourceID']  # resourceKey : 삭제할 폴더/파일의 리소스 키

    elif request.method == 'POST':
        userID = request.POST['userID']
        resourceKey = request.POST['resourceID']

    # 검증 작업 : userID, resourceKey가 데이터베이스에 존재하는지 확인

    userCheck = Users.objects.get(userID=userID)
    resourceCheck = Resources.objects.get(userID=userID, resourceID=resourceKey)
    parentDirID = resourceCheck.parentDirID

    # with transaction.atomic():
        # Transaction start
    # 검증작업을 통과한 경우에만 코드를 실행
    if userCheck and resourceCheck:
        methods = Methods()
        memo = methods.delMemo
        try:
            with transaction.atomic():
                # Transaction start
                # 만약 삭제 대상 리소스의 자식이 없을경우, 삭제 진행
                if resourceCheck.childCount == 0:
                    resourceCheck.delete()
                else:
                    # 삭제의 경우, 상위 폴더를 먼저 삭제할 경우, 하위 리소스를 찾아갈 수 없으므로, memo라는 리스트에 모은 후
                    # 한번에 삭제하는 방식을 선택함.
                    memo.append(resourceCheck)  # memo의 0번째 index == 삭제 대상 폴더 ( 최상위 폴더)
                    memo = collectSubResources(userCheck, resourceCheck.resourceID, memo)
                    memo.pop(0).delete()

            # Transaction finished
        except:
            print("핵심 로직 실패 - roll back")
            return Response(status=404)



        # 나머지 subresource 삭제 (SQL)
        cursor = connection.cursor()
        for i in memo:
            try:
                cursor.execute("DELETE FROM drive_resources WHERE resourceID={0}".format(i.resourceID))
            except:
                methods.requestRawQuery(
                    "DELETE FROM drive_resources WHERE resourceID={0}".format(i.resourceID))

        # 만약 공유된 리소스 인 경우, 공유를 해제함
        if resourceCheck.shareStatus == 'True':
            shareData = resourceCheck.shareID
            # shareUsers 테이블에서 해당 share번호를 가지고 있는 shareusers를 모두 지움
            ShareUsers.objects.filter(shareID=shareData.shareID).delete()
            # share 테이블에서 해당 share 번호를 지움
            shareData.delete()
            timestamp = datetime.datetime.now()
            methods.shareDeleteRequest('rdel_shareDelete', shareData.shareID)

        # 리소스가 삭제 된 부모 폴더에서의 child 수 업데이트
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE drive_resources SET childCount=childCount-1 WHERE resourceID={0};".format(parentDirID))
        except:
            methods.requestRawQuery(
                "UPDATE drive_resources SET childCount=childCount-1 WHERE resourceID={0};".format(parentDirID))

        # 파일 사이즈 업데이트
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE drive_resources SET fileSize=fileSize-{0} WHERE resourceID={1};".format(resourceCheck.fileSize,parentDirID))
        except:
            methods.requestRawQuery(
                "UPDATE drive_resources SET fileSize=fileSize-{0} WHERE resourceID={1};".format(resourceCheck.fileSize,parentDirID))


    timestamp = datetime.datetime.now()
    contents = ''
    fullURL = 'http://localhost:8001/logapi/log/?datetime={0}&type=rdel&userID={1}&parentDirID={2}&contents={3}&resourceID={4}&shareID=0&shareUsersID=0'.format(
        timestamp, userID, parentDirID, contents, resourceKey)
    requestQueue = Background._getInstance()
    requestQueue.put(fullURL)

    resultQuerySet = Resources.objects.filter(userID=userCheck, parentDirID=parentDirID)
    serializer = DriveSerializer(resultQuerySet, many=True)
    return Response(serializer.data)

# 재귀함수를 이용하여 하위 폴더의 총 목록을 memo 리스트에 저장한다.
def collectSubResources(userCheck, resourceID, memo):
    memo = memo
    subResources = Resources.objects.filter(userID=userCheck, parentDirID=resourceID)
    for i in subResources:
        memo.append(i)  # 바로 하위 리소스를 memo 리스트에 추가함.
        if i.childCount == 0: # 해당 하위 리소스가 자식이 없는 경우, continue한다.
            continue
        else :
            collectSubResources(userCheck, i.resourceID, memo) # 만약 해당 하위 리소스에 자식이 있는경우, 같은함수를 한번더 시행한다.

    return memo
