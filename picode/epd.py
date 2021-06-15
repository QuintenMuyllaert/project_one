
from RPi import GPIO
from time import sleep
class EPD:
    def __init__(self, spi,dc,busy):
        self.spi = spi
        self.dc = dc
        self.busy = busy

        self.width = 200
        self.height = 200

        self.b = []
        for i in range(0,self.width):
            self.b.append([])
            for j in range(0,self.height):
                self.b[i].append(0)

        #GPIO.setup(knop,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.dc,GPIO.OUT)
        GPIO.setup(self.busy,GPIO.IN)

        self.spi.open(0,0)
        self.spi.max_speed_hz=1000000

        self.wait_until_idle()
        self.send_command(0x12)  #SWRESET
        self.wait_until_idle()

        self.send_command(0x01) #Driver output control
        self.send_data(0xC7)
        self.send_data(0x00)
        self.send_data(0x01)

        self.send_command(0x11) #data entry mode
        self.send_data(0x01)

        self.send_command(0x44) #set Ram-X address start/end position
        self.send_data(0x00)
        self.send_data(0x18)    #0x0C-->(18+1)*8=200

        self.send_command(0x45) #set Ram-Y address start/end position
        self.send_data(0xC7)   #0xC7-->(199+1)=200
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C) #BorderWavefrom
        self.send_data(0x01)

        self.send_command(0x18)
        self.send_data(0x80)

        self.send_command(0x22) # #Load Temperature and waveform setting.
        self.send_data(0XB1)
        self.send_command(0x20)

        self.send_command(0x4E)   # set RAM x address count to 0
        self.send_data(0x00)
        self.send_command(0x4F)   # set RAM y address count to 0X199
        self.send_data(0xC7)
        self.send_data(0x00)
        self.wait_until_idle()
    
    def turn(self,b,amt):
        for i in range(0,amt):
            b = list(zip(*b[::-1]))
        return b

    
    def send_matrix(self,full = False):
        w =  int(self.width / 8 ) if (self.width % 8 == 0) else int(self.height / 8 + 1)
        h = self.height

        nb = self.turn(self.b,1)

        self.send_command(0x24)
        for j in range(0,h):
            for i in range(0,w):
                r = nb[j]
                dat = 0
                for k in range(0,8):
                    try:
                        dat = dat | ((not r[(i*8)+k]) << 7-k)
                    except:
                        dat = dat | (0 << 7-k)
                self.send_data(dat)
        
        #DISPLAY REFRESH
        self.send_command(0x22)
        self.send_data(0xF7 if full else 0xFF)
        self.send_command(0x20)
        self.wait_until_idle()

    def insert_matrix(self,x,y,mat):
        for i in range(0,len(mat)):
            for j in range(0,len(mat[i])):
                self.b[x+i][y+j] = mat[i][j]


    def send_command(self,cmd):
        GPIO.output(self.dc,0)
        self.spi.writebytes([cmd])

    def send_data(self,cmd):
        GPIO.output(self.dc,1)
        self.spi.writebytes([cmd])
    
    def wait_until_idle(self):
        while(GPIO.input(self.busy)):
            sleep(0.1)
        sleep(0.2)
    
    def clear(self):
        w =  int(self.width / 8 ) if (self.width % 8 == 0) else int(self.height / 8 + 1)
        h = self.height
        self.send_command(0x24)
        for j in range(0,h):
            for i in range(0,w):
                self.send_data(0xFF)

        #DISPLAY REFRESH
        self.send_command(0x22)
        self.send_data(0xF7)
        self.send_command(0x20)
        self.wait_until_idle()
