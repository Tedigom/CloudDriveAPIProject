
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

# 3. 파일/폴더 복사(resource copy, rcpy)
@api_view(['GET','POST'])
def resource_copy(request):
    # 상위폴더를 하위폴더에 복사하는지 check하는 flag
    checkingFlag :bool = False

    if request.method == 'GET':

        # Request Parameter : userID, ResourceKey, objectDirectoryKey

        userID = request.GET['userID']  # UserID : 사용 유저 ID
        resourceKey = request.GET['resourceID']  # resourceKey : 복사할 원본 폴더/파일의 리소스 키
        objectDirectoryKey = request.GET['parentDirID']  # 복사 대상 폴더의 리소스 키

    elif request.method == 'POST':
        userID = request.POST['userID']
        resourceKey = request.POST['resourceID']
        objectDirectoryKey = request.POST['parentDirID']


    # 검증 작업 : userID, resourceKey,objectDirectoryKey가 데이터베이스에 존재하는지 확인
    userCheck = Users.objects.get(userID = userID)
    resourceCheck = Resources.objects.get(userID = userID, resourceID = resourceKey)
    dirCheck = Resources.objects.get(userID= userID, resourceID = objectDirectoryKey)

    # 검증작업을 통과한 경우에만 코드를 실행
    # with transaction.atomic():
        # Transaction Start
    if userCheck and resourceCheck and dirCheck:
        methods = Methods()
        memo = methods.copyMemo
        copyResourceName = resourceCheck.resourceName

        # 폴더 이름 중복확인 check logic
        # rList는 해당 parentDirID에서 child 리소스들의 resourceName을 QuerySet 형태로 가져온다.
        rList = Resources.objects.filter(userID=userCheck, parentDirID=dirCheck.resourceID).values('resourceName')
        for rName in rList:
            # 새로 생성할 폴더의 이름과, 기존에 있던 리소스의 이름이 같다면,
            if rName['resourceName'] == copyResourceName:
                # 새로 생성할 폴더의 이름을 바꾼다.
                copyResourceName = methods.changeResourceName(copyResourceName, rList)
                break

        # 대상 Resource에 대하여 copy 진행

        try:
            with transaction.atomic():
                # Transaction start
                copyResource = Resources(userID=userCheck, resourceName=copyResourceName,
                                         parentDirID=dirCheck.resourceID,
                                         fullPath=dirCheck.fullPath + '/' + copyResourceName,
                                         fileSize=resourceCheck.fileSize, fileType=resourceCheck.fileType,
                                         childCount=resourceCheck.childCount, shareID=resourceCheck.shareID,
                                         shareStatus=resourceCheck.shareStatus)

                copyResource.save()

                # 만약 copy 대상이 하위 폴더가 있는 폴더일 경우, 폴더 내 하위 폴더에 대해서도 복사를 진행해야한다.
                if copyResource.fileType == 'Directory' and copyResource.childCount > 0:

                    # 상위 폴더를 하위폴더 내에 복사하는 것을 막기위해 dirCheck의 parentID를 추적하여 memo에 추가한다.
                    memo.append(dirCheck.parentDirID)
                    while True:
                        checkingResourceID = memo[-1]
                        if checkingResourceID == 'root':
                            break
                        elif checkingResourceID == str(resourceCheck.resourceID):
                            print("상위 폴더를 하위폴더 내에 복사하는 행위")
                            checkingFlag = True
                            try:
                                copyResource.delete()
                            except:
                                timestamp = datetime.datetime.now()
                                methods.resourceDeleteRequest('del', copyResource.resourceID, timestamp)
                            return JsonResponse({'message': 'Can not copy parent folder into subfolder.'})

                        else:
                            parent = Resources.objects.get(userID=userID, resourceID=checkingResourceID)
                            memo.append(parent.parentDirID)

                    # 만약 상위 폴더를 하위폴더내에 복사하는 것이 아니라면, copysubResources를 실행한다.
                    if checkingFlag == False:
                        copySubResources(resourceCheck.resourceID, userCheck, copyResource.resourceID,
                                         copyResource.fullPath, methods)


        except:
            # methods.resourceCreateRequest('rcpy1',userID,copyResourceName,dirCheck.resourceID,dirCheck.fullPath + '/' + copyResourceName,resourceCheck.fileSize,
            #                               resourceCheck.fileType,resourceCheck.childCount,resourceCheck.shareStatus,resourceCheck.shareID)
            print("핵심로직 실패 - rollback")
            return Response(status=404)

        try :
            cursor = connection.cursor()
            cursor.execute("UPDATE drive_resources SET fileSize=fileSize+{0} WHERE resourceID={1};".format(copyResource.fileSize,copyResource.parentDirID))
        except:
            methods.requestRawQuery("UPDATE drive_resources SET fileSize=fileSize+{0} WHERE resourceID={1};".format(copyResource.fileSize,copyResource.parentDirID))
        try :
            # 리소스가 복사 된 부모 폴더에서의 child 수 업데이트
            cursor = connection.cursor()
            cursor.execute("UPDATE drive_resources SET childCount=childCount+1 WHERE resourceID={0};".format(dirCheck.resourceID))
        except:
            methods.requestRawQuery("UPDATE drive_resources SET childCount=childCount+1 WHERE resourceID={0};".format(dirCheck.resourceID))


    timestamp = datetime.datetime.now()
    contents = ''
    fullURL = 'http://localhost:8001/logapi/log/?datetime={0}&type=rcpy&userID={1}&parentDirID={2}&contents={3}&resourceID={4}&shareID=0&shareUsersID=0'.format(
        timestamp, userID, objectDirectoryKey, contents, resourceKey)
    requestQueue = Background._getInstance()
    requestQueue.put(fullURL)

    queryset = Resources.objects.filter(userID=userCheck, parentDirID=dirCheck.resourceID)
    serializer = DriveSerializer(queryset, many=True)
    return Response(serializer.data)


# 하위 폴더 복사하는 메서드 - 재귀함수 사용
# 첫번째 인자 : subresource의 부모 , 두번재인자 : usercheck, 세번째 인자 : subresource가 복제될 때, 필요한 복제된 부모 copyID
def copySubResources(parentDirID, userCheck,copyID, fullPath,methods):
    resourceQuerySet = Resources.objects.filter(userID=userCheck, parentDirID=parentDirID)
# QuerySet을 List로 변환함.
    resourceList = []
    for i in resourceQuerySet:
        resourceList.append(i)


    for i in range(len(resourceList)):
        copyResource = Resources(userID=resourceList[i].userID, resourceName=resourceList[i].resourceName,
                                parentDirID=copyID,
                                fullPath=fullPath + '/' + resourceList[i].resourceName, fileSize=resourceList[i].fileSize,
                                fileType=resourceList[i].fileType, childCount=resourceList[i].childCount,
                                shareID=resourceList[i].shareID, shareStatus=resourceList[i].shareStatus)
        copyResource.save()


        if copyResource.fileType == 'Directory'and copyResource.childCount > 0:
            copySubResources(resourceList[i].resourceID, resourceList[i].userID, copyResource.resourceID, copyResource.fullPath)
        else:
            print("파일이거나, childcount가 0")
