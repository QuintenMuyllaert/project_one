import math
from time import sleep 
class LEDS:
    def __init__(self,amt,ser):
        self.amt = amt
        self.leds = []
        self.effect = "solid"

        self.h = 0
        self.s = 255
        self.b = 50

        self.ser = ser
        print(self.ser.name)
        self.ser.flush()

        for i in range(0,self.amt):
            self.leds.append([0,0,0])

        self.ser.write(bytes("\n","utf-8"))

    def led2D(self,x,y,h,s,b):
        #x = (x + 14) % 140
        self.set_led(math.floor((x%15)+(y%22)*14.35),h,s,b)

    def hexString(self,inp):
        return (str(hex(inp)) if len(str(hex(inp))) > 3 else "0x0" + str(hex(inp)).split("0x")[1]).replace("0x","").upper()


    def set_led(self,index,h,s,b):
        if index>=self.amt:
            return
        self.leds[round(index)%len(self.leds)] = [round(h)%256,round(s)%256,round(b)%256]

    def send(self):
        txt = ""
        for i in range(0,self.amt):
            txt+=self.hexString(self.leds[i][0])+self.hexString(self.leds[i][1])+self.hexString(self.leds[i][2])
            if(i % 100==99):
                self.ser.write(bytes(txt+"\r","utf-8"))
                txt = ""
                sleep(0.0075)
        self.ser.write(bytes("\n","utf-8"))        
       
        #self.ser.write(bytes("00FFFF"*100+"\r","utf-8"))
        #sleep(0.1)
        #self.ser.write(bytes("80FFFF"*100+"\r","utf-8"))
        #sleep(0.1)
        #self.ser.write(bytes("00FFFF"*100+"\r\n","utf-8"))   
