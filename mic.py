from time import sleep
class MIC:
    def __init__(self, ser):
        self.ser = ser
        self.hex_map = { #Python hurts my soul.
            "0":0,
            "1":1,
            "2":2,
            "3":3,
            "4":4,
            "5":5,
            "6":6,
            "7":7,
            "8":8,
            "9":9,
            "A":10,
            "B":11,
            "C":12,
            "D":13,
            "E":14,
            "F":15   
        }
        self.pulses = 0

    def read(self):
        self.ser.flush()
        self.ser.write(bytes("P","utf-8"))
        try:
            line = str(self.ser.readline().decode().replace('\r\n',''))
            if line != "":
                pulses = 0
                for i in range(0,len(line)):
                    pulses = pulses | int(self.hex_map[line[i]]) << 4
                self.pulses = pulses
        except:
            print("mic fail")
        return self.pulses