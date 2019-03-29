from rest_framework.decorators import api_view
from rest_framework.response import Response

from drive.serializers import DriveSerializer
from drive.models import Resources, Users, Shares, ShareUsers
from drive.viewsMethod import Methods
from drive.background import Background

import datetime
import requests

from django.db import transaction, connection


# 2. 폴더생성(make directory, mkdir)
@api_view(['GET','POST'])
def make_directory(request):
    if request.method == 'GET':

    # Request Parameter : userID, parentDirID(ResourceKey), folderName

        userID = request.GET['userID']      # UserID : 사용 유저 ID
        parentDirID = request.GET['parentDirID']    # parentDirID : 부모 폴더의 키
        folderName = request.GET['folderName']      # folderName : 생성할 폴더의 이름

    elif request.method == 'POST':
        userID = request.POST['userID']
        parentDirID = request.POST['parentDirID']
        folderName = request.POST['folderName']

    # 검증 작업 : userID, parentDirID가 데이터베이스에 존재하는지 확인
    userCheck = Users.objects.get(userID = userID)
    dirCheck = Resources.objects.get(userID= userID, resourceID = parentDirID)

    # 검증작업을 통과한 경우에만 코드를 실행
    # with transaction.atomic():
    #     #Transaction start
    if dirCheck and userCheck:
        methods = Methods()
        # 폴더 이름 중복확인 check logic
        # dirList는 해당 parentDirID에서 child 리소스들의 resourceName을 QuerySet 형태로 가져온다.
        dirList = Resources.objects.filter(userID=userCheck, parentDirID=parentDirID).values('resourceName')
        for dirName in dirList:
            # 새로 생성할 폴더의 이름과, 기존에 있던 리소스의 이름이 같다면,
            if dirName['resourceName'] == folderName:
                # 새로 생성할 폴더의 이름을 바꾼다.
                folderName = methods.changeResourceName(folderName, dirList)
                break
        try :
            with transaction.atomic():
                #Transaction start
                # 폴더 생성
                newFolder = Resources(userID= userCheck, resourceName=folderName, parentDirID=parentDirID,
                                    fullPath=dirCheck.fullPath + '/'
                                            + folderName, fileSize=0, fileType='Directory', shareID=None,
                                    shareStatus='False')
                # 폴더 객체를 데이터베이스에 저장
                newFolder.save()
        except:
            # methods.resourceCreateRequest('mkdir1',userID,folderName,parentDirID,dirCheck.fullPath + '/' + folderName,0,'Directory',0,'False',None)
            print("핵심 로직 실패 -> rollback")
            return Response(status=404)
        try:
            # 폴더 생성된 부모 폴더에서의 child 수 업데이트
            # methods.addChildCount(parentDirID, userCheck)
            cursor = connection.cursor()
            cursor.execute("UPDATE drive_resources SET childCount=childCount+1 WHERE resourceID={0};".format(parentDirID))
        except:
            methods.requestRawQuery("UPDATE drive_resources SET childCount=childCount+1 WHERE resourceID={0};".format(parentDirID))
    else:
        print("newfolder 생성 안됨")
        return Response(status=404)

    timestamp = datetime.datetime.now()
    contents = 'foldername={0}'.format(folderName)
    fullURL = 'http://localhost:8001/logapi/log/?datetime={0}&type=mkdir&userID={1}&parentDirID={2}&contents={3}&resourceID=0&shareID=0&shareUsersID=0'.format(
        timestamp, userID, parentDirID, contents)
    requestQueue = Background._getInstance()
    requestQueue.put(fullURL)

        # Transaction finished

    queryset = Resources.objects.filter(userID=userCheck, parentDirID=parentDirID)
    serializer = DriveSerializer(queryset, many=True)

    return Response(serializer.data)
