from .models import Resources, Users
from .background import Background
import uuid
import datetime


class Methods(object):

    copyMemo = []
    delMemo = []

    def __init__(self):
        self.copyMemo = []
        self.delMemo = []

    # django ORM 에서 filter를 쓰는 경우, Queryset 형태로 값이 들어오게 된다. ex) querySet { ['A':'1'], ['A':'2']...}
    # 한가지 key에 대한 (example 에서는 'A'값) value들의 list를 쓰기 위해 querySetToList라는 method를 만들었다.

    def querySetToList(self,querySet, key):
        valueList = []
        for i in querySet:
            valueList.append(i[key])
        return valueList

    # API List 중 '폴더 생성(mkdir)', '폴더 복사 (rcpy)', '폴더 이동(rmv)' 에서 폴더 생성시에 이미 같은 이름의 foldername이 있을 경우 생성되는 폴더의 이름을
    # 다르게 만들어주는 메서드를 만들었다.
    # testFolder , testFolder_1 , testFolder_2 , testFolder_3 ... 과 같은 형태로 네이밍된다.

    def changeResourceName(self, resourceName, resourceList):
        nameList = self.querySetToList(resourceList,'resourceName')
        i = 1
        newResourceName = resourceName + '_' + str(i)
        while (True):
            if newResourceName in nameList :
                i += 1
                newResourceName = resourceName + '_' + str(i)
            else:
                break
        return newResourceName


    def addChildCount(self,parentDirID, userCheck):
        parentDir = Resources.objects.get(resourceID = parentDirID,userID = userCheck)
        parentDir.childCount += 1
        parentDir.revision = 1
        parentDir.save()


    def subtractChlidCount(self,parentDirID, userCheck):
        parentDir = Resources.objects.get(resourceID = parentDirID,userID = userCheck)
        parentDir.childCount -= 1
        parentDir.revision = 1
        parentDir.save()


    def updateFileSize(self,parentDirID, userCheck,fileSize):
        parentDir = Resources.objects.get(resourceID = parentDirID,userID = userCheck)
        while True:
            parentDir.fileSize += int(fileSize)
            parentDir.save()
            if parentDir.parentDirID == 'root':
                break
            else:
                parentDir = Resources.objects.get(userID= userCheck, resourceID = parentDir.parentDirID)


    def subtractFileSize(self,parentDirID, userCheck, fileSize):
        parentDir = Resources.objects.get(resourceID=parentDirID, userID=userCheck)
        while True:
            parentDir.fileSize -= int(fileSize)
            parentDir.save()
            if parentDir.parentDirID == 'root':
                break
            else:
                parentDir = Resources.objects.get(userID=userCheck, resourceID=parentDir.parentDirID)

    def makeUUID(self):
        uuidvalue = uuid.uuid4()
        return uuidvalue

    # ResoruceRequests
    def resourceCreateRequest(self, type, userID, resourceName, parentDirID, fullPath, fileSize, fileType, childCount, shareStatus, shareID):
        timestamp = datetime.datetime.now()
        fullURL = 'http://localhost:8002/api/errorHandling/?type={0}&userID={1}&resrouceName={2}&parentDirID={3}&fullPath={4}&fileSize={5}&fileType={6}&childCount={7}&shareStatus={8}&shareID={9}&timeStamp={10}'.format(type,
                   userID, resourceName, parentDirID, fullPath, fileSize, fileType, childCount, shareStatus, shareID, timestamp)
        requestQueue = Background._getInstance()
        requestQueue.put(fullURL)

    def resourceUpdateRequest(self,type,resourceID,contents):
        timestamp = datetime.datetime.now()
        fullURL = 'http://localhost:8002/api/errorHandling/?type={0}&resourceID={1}&contents={2}&timestamp={3}'.format(type,resourceID,contents,timestamp)
        requestQueue = Background._getInstance()
        requestQueue.put(fullURL)

    def resourceDeleteRequest(self,type,resourceID):
        timestamp = datetime.datetime.now()
        fullURL = 'http://localhost:8002/api/errorHandling/?type={0}&resourceID={1}&timestamp={2}'.format(type, resourceID,timestamp)
        requestQueue = Background._getInstance()
        requestQueue.put(fullURL)

    # ShareRequests
    def shareCreateRequest(self, type, resourceID, resourceName, shareDateTime):
        timestamp = datetime.datetime.now()
        fullURL = 'http://localhost:8002/api/errorHandling/?type={0}&resourceID={1}&resourceName={2}&shareDateTime={3}&timestamp={4}'.format(type,resourceID,resourceName,shareDateTime,timestamp)
        requestQueue = Background._getInstance()
        requestQueue.put(fullURL)

    def shareDeleteRequest(self,type, shareID):
        timestamp = datetime.datetime.now()
        fullURL = 'http://localhost:8002/api/errorHandling/?type={0}&shareID={1}&timestamp={2}'.format(type,shareID,timestamp)
        requestQueue = Background._getInstance()
        requestQueue.put(fullURL)

    # ShareUsers Requests
    def shareUserCreateRequest(self,type,shareID,userID,authority):
        timestamp = datetime.datetime.now()
        fullURL = 'http://localhost:8002/api/errorHandling/?type={0}&shareID={1}&userID={2}&authority={3}&timestamp={4}'.format(type,shareID,userID,authority,timestamp)
        requestQueue = Background._getInstance()
        requestQueue.put(fullURL)

    def shareUserDeleteRequest(self,type, shareID):
        timestamp = datetime.datetime.now()
        fullURL = 'http://localhost:8002/api/errorHandling/?type={0}&shareID={1}&timestamp={2}'.format(type,shareID,timestamp)
        requestQueue = Background._getInstance()
        requestQueue.put(fullURL)


    # ResoruceRequests - Raw Queries

    def requestRawQuery(self,query):
        timestamp = datetime.datetime.now()
        fullURL = 'http://localhost:8001/logapi/errorHandling/?query={0}&timestamp={1}'.format(query,timestamp)
        requestQueue = Background._getInstance()
        requestQueue.put(fullURL)