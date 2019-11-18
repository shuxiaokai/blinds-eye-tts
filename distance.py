import serial
import time
# import concurrent.futures
import threading
import sys


class Distance:
    def __init__(self):
        self.distance = ""
        self.stop_thread = 0
        self.start()
                
    def start(self):
        self.arduino = serial.Serial('/dev/ttyACM0', 9600)
        self.distance_thread = threading.Thread(target=self.calculate)
        self.distance_thread.start()

    def stop(self):
        self.stop_thread = 1
        self.distance = 0
        self.arduino.close()

    def get_distance(self):
        return str(self.distance.replace('\r', '').replace('\n', ''))

    def calculate(self):
        while True:
            if (self.arduino.inWaiting()>0 and self.stop_thread == 0):
                self.distance = self.arduino.readline().decode('ascii')
            elif self.stop_thread == 1:
                break


