from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from drive.serializers import DriveSerializer
from drive.models import Resources, Users, Shares, ShareUsers
from drive.viewsMethod import Methods
from drive.background import Background

from django.http import JsonResponse
import datetime
import requests

from django.db import transaction, connection



## 리소스 업로드 쪽은 단일 파일 업로드에 대해서만 생각함. ( 폴더인 경우에 대해서는 생각하지 않음 )
# 7. 리소스 업로드(resource upload, rupld)
@api_view(['GET','POST'])
def resource_upload(request):

    if request.method == 'GET':

        # Request Parameter : userID, objectDirectoryKey, resourceName

        userID = request.GET['userID']  # UserID : 사용 유저 ID
        objectDirectoryKey = request.GET['parentDirID']  # 업로드 대상 폴더의 리소스 키
        resourceName = request.GET['resourceName'] # 업로드 리소스의 이름
        resourceType = request.GET['resourceType'] # 업로드 리소스의 타입(파일인지 폴더인지)
        fileSize = request.GET['fileSize'] # 업로드 리소스의 파일 사이즈

    elif request.method == 'POST':
        userID = request.POST['userID']
        objectDirectoryKey = request.POST['parentDirID']
        resourceName = request.POST['resourceName']
        resourceType = request.POST['resourceType']
        fileSize = request.POST['fileSize']

    # 검증 작업 : userID, resourceKey,objectDirectoryKey가 데이터베이스에 존재하는지 확인
    userCheck = Users.objects.get(userID = userID)
    dirCheck = Resources.objects.get(userID= userID, resourceID = objectDirectoryKey)

    # with transaction.atomic():
        # transaction start
    # 검증작업을 통과한 경우에만 코드를 실행
    if userCheck and dirCheck:
        methods = Methods()
        # 폴더 이름 중복확인 check logic
        # rList는 해당 parentDirID에서 child 리소스들의 resourceName을 QuerySet 형태로 가져온다.
        rList = Resources.objects.filter(userID=userCheck, parentDirID=dirCheck.resourceID).values('resourceName')
        for rName in rList:
            # 새로 생성할 폴더의 이름과, 기존에 있던 리소스의 이름이 같다면,
            if rName['resourceName'] == resourceName:
                # 새로 생성할 폴더의 이름을 바꾼다.
                resourceName = methods.changeResourceName(resourceName, rList)
                break

        # 대상 Resource에 대하여 upload 진행
        try:
            with transaction.atomic():
                uploadResource = Resources(userID=userCheck, resourceName=resourceName,
                                        parentDirID=dirCheck.resourceID,
                                        fullPath=dirCheck.fullPath + '/' + resourceName,
                                        fileSize=fileSize, fileType=resourceType,
                                        childCount=0, shareID=None,
                                        shareStatus='False')
                uploadResource.save()
        except:
            print("핵심로직 실패 - roll back")
            return Response(status=404)

        try:
            # 리소스가 복사 된 부모 폴더에서의 child 수 업데이트
            cursor = connection.cursor()
            cursor.execute("UPDATE drive_resources SET childCount=childCount+1 WHERE resourceID={0};".format(dirCheck.resourceID))
        except:
            methods.requestRawQuery(
                "UPDATE drive_resources SET childCount=childCount+1 WHERE resourceID={0};".format(dirCheck.resourceID))

        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE drive_resources SET fileSize=fileSize+{0} WHERE resourceID={1};".format(fileSize,dirCheck.resourceID))
        except:
            methods.requestRawQuery("UPDATE drive_resources SET fileSize=fileSize+{0} WHERE resourceID={1};".format(fileSize,dirCheck.resourceID))


    timestamp = datetime.datetime.now()
    contents = 'resourceName={0}|resourceType={1}|fileSize={2}'.format(resourceName, resourceType, fileSize)
    fullURL = 'http://localhost:8001/logapi/log/?datetime={0}&type=rupld&userID={1}&parentDirID={2}&contents={3}&resourceID={4}&shareID=0&shareUsersID=0'.format(
        timestamp, userID, objectDirectoryKey, contents, uploadResource.resourceID)
    requestQueue = Background._getInstance()
    requestQueue.put(fullURL)

    queryset = Resources.objects.filter(userID=userCheck, parentDirID=dirCheck.resourceID)
    serializer = DriveSerializer(queryset, many=True)
    return Response(serializer.data)