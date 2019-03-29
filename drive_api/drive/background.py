from multiprocessing import Queue
import requests
from time import sleep

class Background:
    requestQueue = Queue()

    @classmethod
    def _getInstance(cls):
        return cls.requestQueue

def sendRequest(queue):
    while True:
        if queue.qsize() != 0:
            data = queue.get()
            print("리퀘스트 보냄", data)
            try:
                response = requests.get(data, timeout = 3)
            except:
                print("send Request 예외처리")

        else:
            # print("리퀘스트 없음")
            sleep(5)

def verificationCall():
    while True:
        fullURL = 'http://localhost:8002/api/verification'
        fullURL2= 'http://localhost:8002/api/errorHandling'
        try:
            response = requests.get(fullURL, timeout = 3)
            response2= requests.get(fullURL2, timeout = 3)
            sleep(300)
        except:
            # print("verification 예외처리")
            sleep(300)