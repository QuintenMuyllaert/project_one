import threading
from time import sleep
class TMP:
    def __init__(self):
        self.temp = 0.0
        sensor_file_name = "/sys/bus/w1/devices/28-012033559f07/w1_slave"
        def loop_tempread():
            while True:
                sensor_file = open(sensor_file_name,"r")
                content = float(sensor_file.read().splitlines()[1].split("t=")[1]) / 1000.0
                self.temp = float(content)
                sensor_file.close()
                sleep(0.5)
        x = threading.Thread(target=loop_tempread)
        x.start()
            
    def read(self):
        return self.temp