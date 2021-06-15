from time import sleep
class DHT11:
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
        self.temp = 0.0
        self.humi = 0

    def read(self):
        print("reqing")
        self.ser.flush()
        self.ser.write(bytes("S\n","utf-8"))
        sleep(0.1)
        try:
            line = str(self.ser.readline().decode().replace('\n',''))
            print(f"{line}")
            
            if line != "":
                Humi = int(self.hex_map[line[0]]) << 4 | int(self.hex_map[line[1]])
                Temp = int(self.hex_map[line[2]]) << 4 | int(self.hex_map[line[3]]) 
                Temp_Comma = int(self.hex_map[line[4]]) << 4 | int(self.hex_map[line[5]])
                Temp_Float = float(str(Temp) + "." + str(Temp_Comma))
                self.temp = Temp_Float
                self.humi = Humi
        except:
            print("dht fail")
        return {"temp":self.temp,"humi":self.humi}