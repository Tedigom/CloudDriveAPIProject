import sys
from django.apps import AppConfig
from drive.background import *
from multiprocessing import Process

class DriveConfig(AppConfig):
    name = 'drive'
    def ready(self):
        if 'runserver' not in sys.argv:
            return True
        pass
        requestQueue = Background._getInstance()
        process_one = Process(target=sendRequest, args=(requestQueue,))
        process_two = Process(target=verificationCall)
        process_one.start()
        process_two.start()
