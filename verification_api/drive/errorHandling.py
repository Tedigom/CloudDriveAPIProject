from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Error
from django.db import connections

# Create your views here.
@api_view(['GET'])   # HTTP Method : GET
def errorHandling(request):
    errorQuerySet = Error.objects.using('drivelog').all()
    print(errorQuerySet)
    errorList = []
    for i in errorQuerySet:
        errorList.append(i)

    cursor = connections['drive'].cursor()
    print(cursor)
    for i in range(len(errorList)):
        error = errorList[i]
        # try:
        errorQuery = error.errorQuery
        print("에러쿼리값:", errorQuery)
        cursor.execute("{0}".format(errorQuery))
        Error.objects.using('drivelog').filter(errorQuery = errorQuery).delete()
        print("TEST")

        # except:
        #     print("에러 처리 안됨")


    print("에러 처리 완료")
    return Response(status=200)