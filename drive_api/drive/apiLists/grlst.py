from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from drive.serializers import DriveSerializer
from drive.models import Resources, Users, Shares, ShareUsers



# 1. 리소스 목록 조회(get resource list/ grlst)
@api_view(['GET','POST'])   # HTTP Method : GET, POST
def get_resource_list(request):
    if request.method == 'GET':

        # Request Parameter : UserID, parentDirID(Resource Key), sort, sortOrder

        userID = request.GET['userID']      # UserID : 사용 유저 ID
        parentDirID = request.GET['parentDirID']    # parentDirID : 부모 폴더 키
        sort = request.GET['sort']  # sort : 정렬 조건 : 생성일, 수정일, 이름
        sortOrder = request.GET['sortOrder']    # sortOrder : 정렬 순서(ASC, DESC)

    elif request.method == 'POST':
        userID = request.POST['userID']
        parentDirID = request.POST['parentDirID']
        sort = request.POST['sort']
        sortOrder = request.POST['sortOrder']

    # 검증 작업 : userID, parentDirID가 데이터베이스에 존재하는지 확인
    userCheck = Users.objects.get(userID=userID)
    dirCheck = Resources.objects.filter(userID=userID, resourceID= parentDirID)

    # 검증작업을 통과한 경우에만 코드를 실행
    if dirCheck and userCheck:
        # DESC 의 조건,
        if sortOrder == 'DESC':
            # ORM : SELECT문 실행 ( Where 조건: userID = userID and parentDirID = parentDirID         //   내림차순)
            queryset = Resources.objects.filter(userID= userID, parentDirID = parentDirID).order_by('-'+sort)
        # ASC 의 조건
        else:
            # ORM : SELECT문 실행 ( Where 조건: userID = userID and parentDirID = parentDirID         //   오름차순)
            queryset = Resources.objects.filter(userID=userID, parentDirID = parentDirID).order_by(sort)

    else :
        print("error occured")
        return Response(status=404)


    serializer = DriveSerializer(queryset, many=True)
    return Response(serializer.data)
