from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Log,Resources, Users, Shares
from django.db.models import Q
import datetime

# Create your views here.
@api_view(['GET','POST'])   # HTTP Method : GET, POST
def verification(request):
    time = CheckingTime.checkingTime
    #log 불러옴 ( 검증 대상을 일반 로그와 Delete 대상 로그로 나눔),지난 업데이트 datetime 이후 로그로 한정함.
    veri = Log.objects.using('drivelog').filter(logDateTime__gte = time).order_by('logDateTime')
    veriDel = Log.objects.using('drivelog').filter(logDateTime__gte=time, logType = 'rdel').order_by('logDateTime')

    # resource table 검증대상 : veriDelList : 삭제된 대상의 resourceID , veriList : veriDelList를 제외한 resourceID 및 parentDirID
    veriDelList = set(i.logResourceID for i in veriDel)
    veriList = set(i.logResourceID for i in veri).union(set(i.logParentDirID for i in veri))-veriDelList
    veriList.discard(0)
    veriDelResource = Resources.objects.filter(resourceID__in = list(veriDelList))
    veriResource = Resources.objects.filter(resourceID__in = list(veriList)).exclude(parentDirID='root')


    # 삭제된 데이터에 대한 검증
    verificationDeletedRows(veriDelResource)
    # 실존 데이터에 대한 검증
    verificationRows(veriResource)

    # 검증 마지막 로그 기준 시간으로 checking time 업데이트
    CheckingTime.checkingTime = list(veri)[-1].logDateTime
    print("업데이트 된 체킹 타임",CheckingTime.checkingTime)

    return Response(status=200)



def verificationDeletedRows(veriDelResource):
    if veriDelResource.count() == 0:
        print("Delete에 대한 문제 없음")
    else:
        for row in veriDelResource:
            row.delete()


def verificationRows(veriResource):
    for row in veriResource:
        # 중복된 데이터 값에 대한 검증
        if Resources.objects.filter(resourceName = row.resourceName, userID = row.userID,
                                    parentDirID = row.parentDirID, fileSize = row.fileSize,
                                    fullPath = row.fullPath).count() > 1:
            if row.childCount == 0:
                row.delete()
            else:
                print("에러사항 있음.")
                continue
        else:
            print("중복데이터 없음")

        # Row에 대한 데이터 검증
        verificationValueInRow(row)

        print("검증 완료")


def verificationValueInRow(row):
    # 부모 자식 관계가 맞는지에 대한 검증 ( parentID, FullPath를 이용하여 정합성이 맞는지 검증 )
    rowParentDirID = row.parentDirID
    rowFullPath = row.fullPath.split('/')
    rowResourceName = row.resourceName

    print("값들",rowParentDirID,rowFullPath,rowResourceName)

    # 검증 row의 parentDirID가 실재 존재하는지 확인
    try:
        parentResourceName = Resources.objects.get(resourceID = rowParentDirID).resourceName
    except:
        print("검증하는 row의 parentDirID가 존재하지 않는 상황")


   # fullpath와 parentDirID가 일관되는지 확인
    if rowFullPath[-1] == rowResourceName:
        if parentResourceName == rowFullPath[-2]:
            print("row의 데이터가 정상적인 상황")
        else:
            print("Row의 fullpath의 parent 값과 Row의 parentDirID가 맞지 않는 상황")
    else:
        print("Row의 fullPath의 마지막 값이 Row의 resourceName과 맞지 않는 상황")


    # Row 데이터의 Share값에 대한 확인
    if row.shareID == None:
        if row.shareStatus == 'True':
            print("share status에 대한 정합성이 틀린 상황")
            row.shareStatus = 'False'
            row.save()
        else:
            print("share에 대한 문제 없음")
    else:
        try:
            shareResourceID = Shares.objects.get(shareID = row.shareID).resoruceID
            if row.resourceID != shareResourceID:
                print("share ID에 대한 정합성이 틀린 상황 ( Share table의 resource ID와 row의 resourceID가 맞지 않는 상황")
            else:
                print("Share에 대한 문제 없음")
        except:
            print("shareID 에 대한 정합성이 틀린 상황")



class CheckingTime:
    checkingTime = datetime.datetime.strptime('2019-02-11 22:37:42.838156', '%Y-%m-%d %H:%M:%S.%f')



