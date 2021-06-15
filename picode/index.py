import serial
import threading
import math
import datetime
import os

from astral import LocationInfo
from astral.sun import sun
from time import sleep
from random import random
from RPi import GPIO
from spidev import SpiDev 
from PIL import Image, ImageDraw
from flask import Flask, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit

from helper import *
from epd import EPD
from dht import DHT11
from leds import LEDS
from mic import MIC
from tmp import TMP
from db import DATABASE

reset_serial()

hard_serial = serial.Serial("/dev/serial0",500000,timeout=1)
spi = SpiDev() 
GPIO.setmode(GPIO.BCM)

leds = LEDS(300,hard_serial)
epd = EPD(spi,23,24)
dht = DHT11(hard_serial)
mic = MIC(hard_serial)
tmp = TMP()
database = DATABASE()

class APP:
    def __init__(self, port):              
        self.port = port        
        self.app = Flask(__name__)
        self.app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

        self.socketio = SocketIO(self.app)

        @self.app.after_request
        def add_header(r): #Cache is evil, we dont want it in developement!
            r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            r.headers["Pragma"] = "no-cache"
            r.headers["Expires"] = "0"
            r.headers['Cache-Control'] = 'public, max-age=0'
            return r

        @self.app.route("/<path:path>")
        def return_static(path):
            return send_from_directory("public",path)

        @self.app.route("/")
        def return_main():
            landing = open("./public/index.html","r")
            txt = landing.read()
            landing.close()
            return txt

        @self.app.route("/data.json", methods=['GET'])
        def data():
            if request.method == 'GET':
                return jsonify(temp=tmp.temp,humi=dht.humi,effect=leds.effect,hue=leds.h,sat=leds.s,bright=leds.b),200

        @self.app.route("/history.json", methods=['GET'])
        def history():
            if request.method == 'GET':
                now = round(get_time()/1000000)*1000000
                print(get_time(),now)
                one_day = 1000 * 60 * 60 * 24
                data = {
                    "tmp_h":[],
                    "tmp_l":[],
                    "dht_h":[],
                    "dht_l":[],
                    "time":[],
                }
                for i in range(0,7):
                    dht_low = database.get_one_row(f"SELECT * FROM DHT WHERE time > {now - (i * one_day)} AND time < {now + one_day - (i * one_day)} ORDER BY humidity ASC LIMIT 1;","") #low
                    dht_high = database.get_one_row(f"SELECT * FROM DHT WHERE time > {now - (i * one_day)} AND time < {now + one_day - (i * one_day)} ORDER BY humidity DESC LIMIT 1;","") #high
                    tmp_low = database.get_one_row(f"SELECT * FROM TMP WHERE time > {now - (i * one_day)} AND time < {now + one_day - (i * one_day)} ORDER BY temperature ASC LIMIT 1;","") #low
                    tmp_high = database.get_one_row(f"SELECT * FROM TMP WHERE time > {now - (i * one_day)} AND time < {now + one_day - (i * one_day)} ORDER BY temperature DESC LIMIT 1;","") #high
                    
                    try:
                        data["tmp_h"].append(tmp_high["temperature"])
                        data["tmp_l"].append(tmp_low["temperature"])
                    except:
                        data["tmp_h"].append(None)
                        data["tmp_l"].append(None)
                    try:
                        data["dht_h"].append(dht_high["humidity"])
                        data["dht_l"].append(dht_low["humidity"])
                    except:
                        data["dht_h"].append(None)
                        data["dht_l"].append(None)
                    data["time"].append(get_time() - (i * one_day))
                return jsonify(data),200


        @self.socketio.on('time')
        def set_date_ev(json):
            print('time: ' + str(json))
            if(check_string(str(json))):
                psw = open("./psw.txt")
                os.system(f"echo {psw.read()} | sudo -S date -s \"{json}\"")
                psw.close()

        @self.socketio.on('solid')
        def solid_ev(json):
            print('received json: ' + str(json))
            leds.h = round(json["h"])
            leds.s = round(json["s"])

        @self.socketio.on('setEffect')
        def leds_effect_ev(json):
            print("new effect",json)
            for i in range(0,300):
                leds.set_led(i,0,0,0)
            
            if(json in  effects.keys()):
                leds.effect = json
            emit('setEffect', json ,broadcast=True)


        @self.socketio.on('dht')
        def dht_ev(json):
            emit('weather', {"temp":tmp.temp,"humi":dht.humi})

        @self.socketio.on('brightness')
        def dht_ev(json):
            print(json)
            leds.b =  0 if int(json)%256 == 25 else int(json)%256
            emit('brightness', leds.b ,broadcast=True)

    def start_server(self):
        print("starting")
        def open_server(a):
            self.socketio.run(self.app,host="0.0.0.0",port=self.port)
        self.x = threading.Thread(target=open_server, args=(1,))
        self.x.start()

if __name__ == '__main__':
    app = APP(8080)
    app.start_server()

def run_epd():
    print("starting epd")
    img = Image.new('RGB', (120, 30), color = (0, 0, 0))
    d = ImageDraw.Draw(img)
    try:
        d.text((0,0), f"{read_ips()[0]}\n{read_ips()[1]}", fill=(255,255,255))
    except:
        d.text((0,0), f"{read_ips()[0]}", fill=(255,255,255))
    image = Image.open("background.png", "r")
    back = image2D(image)

    letter = image2D(img)

    epd.insert_matrix(0,0,back)
    epd.insert_matrix(8,8,letter)

    epd.send_matrix(True)
    print("done epd")

    while True:
        img = Image.new('RGB', (120, 30), color = (0, 0, 0))
        d = ImageDraw.Draw(img)
        try:
            d.text((0,0), f"{read_ips()[0]}\n{read_ips()[1]}", fill=(255,255,255))
        except:
            d.text((0,0), f"{read_ips()[0]}", fill=(255,255,255))
        epd.send_matrix(False)
        sleep(1)

x = threading.Thread(target=run_epd)
x.start()

def zons_onder():
    if((frames % (0.1 * one_sec)) == 0):
        for i in range(0,300):
            leds.set_led(i,60,255,127)
        for i in range(0,15):
            for k in range(0,15):
                if(k<5):
                    leds.led2D(i,k,(240)+round(random()*10),255,200)
                elif(k<10):
                    leds.led2D(i,k,(1)+round(random()*10),255,200) 
                else:
                    leds.led2D(i,k,(20)+round(random()*10),255,127)
        leds.send()


def off(send=True):
    if((frames % (0.1 * one_sec)) == 0):
        for i in range(0,300):
            leds.set_led(i,0,0,0)
        if(send):
            leds.send()

def solid():
    if((frames % (0.1 * one_sec)) == 0):
        for i in range(0,300):
            leds.set_led(i,leds.h,leds.s,leds.b)
        leds.send()

orbit_speeds = [0,0,0,0,0,0,0]
def orbit():
    if((frames % (0.1 * one_sec)) == 0):
        if(orbit_speeds[0] == 0):
            for i in range(0,len(orbit_speeds)):
                orbit_speeds[i] = random()
        
        j = round(frames/10)
        for i in range(0,300):
            leds.set_led(i,70,255,30)        

        for i in range(0,len(orbit_speeds)):
            spd = round(j * orbit_speeds[i])
            if(spd%42<21):
                leds.set_led(i*2+(spd%21)*14,i * 45,255,255)
            else:
                leds.set_led(i*2+(21-(spd%21))*15+9,i * 45,255,255)
        
        leds.send()
    
def test():
    j = round(frames/10)
    if((frames % (0.1 * one_sec)) == 0):
        for i in range(0,300):
            leds.set_led(i,0,255 * ((j%300) == i),127)
                
        leds.send()

def fade():
    j = round(frames/10)
    if((frames % (0.1 * one_sec)) == 0):
        for i in range(0,300):
            leds.set_led(i,50*(1+math.sin((i+frames)/200)) + leds.h,255,127)
                
        leds.send()

drops = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
def rain():
    if((frames % (0.1 * one_sec)) == 0):
        drop_id = round(14*random())
        if(drops[drop_id] == -1): 
            drops[drop_id] = 17
                
        for i in range(0,len(drops)):
            if(not(drops[i] == -1)):
                leds.led2D(i,drops[i]+2,0,0,0)
                leds.led2D(i,drops[i]+1,60,255,80)
                leds.led2D(i,drops[i],90,255,127)
                drops[i]-=1
            else:
                leds.led2D(i,0,0,0,0)
                leds.led2D(i,1,0,0,0)
                

        for i in range(0,15):
            for j in range(0,3):
                if round(random()*4) == 0:
                    leds.led2D(i,20-j,80,40*int(random()<0.2),30+round(random()*80))

        leds.send()

def steam():
    if((frames % (0.1 * one_sec)) == 0):
        drop_id = round(14*random())
        if(drops[drop_id] == -1): 
            drops[drop_id] = 18
        
        for i in range(0,300):
            if(random()<0.2):
                leds.set_led(i,0,100+round(random()*155),round(random()*255))
            elif(random()<0.2):
                leds.set_led(i,0,0,0)
            
                
        for i in range(0,len(drops)):
            if(not(drops[i] == -1)):
                leds.led2D(i,22-drops[i],0,0,127)
                leds.led2D(i,22-drops[i]+1,0,0,127)
                leds.led2D(i,22-drops[i]+2,90,0,255)
                drops[i]-=1
            else:
                leds.led2D(i,0,0,0,0)
                leds.led2D(i,1,0,0,0)
                

        for i in range(0,15):
            for j in range(0,3):
                if round(random()*4) == 0:
                    leds.led2D(i,20-j,80,40*int(random()<0.2),30+round(random()*80))

        leds.send()

def sound():
    if((frames % (0.1 * one_sec)) == 0):
        loudness = mic.read()
        for i in range(0,300):
            #leds.set_led(i,leds.h,leds.s,300-(i*loudness)) #VERY COOL
            leds.set_led(i,leds.h + (loudness/10) *(i / 300),255,300-(i*loudness))
        leds.send()
        leds.h += round(loudness/10)

def rainbow_sound():
    if((frames % (0.1 * one_sec)) == 0):
        loudness = mic.read()
        for i in range(0,300):
            #leds.set_led(i,leds.h,leds.s,300-(i*loudness)) #VERY COOL
            leds.set_led(i,leds.h + (loudness/10) *(i / 300) + 300-(i+5*loudness),255,300-(i*loudness))
        leds.send()
        leds.h += round(loudness/10)

def automatic():
    if((frames % (0.1 * one_sec)) == 0):
        city = LocationInfo("Brussels", "Belgium")
        now = datetime.datetime.now()
        
        s = sun(city.observer, date=datetime.date(now.year, now.month, now.day))
        dawn = s["dawn"]
        sunrise = s["sunrise"]
        noon = s["noon"]
        sunset = s["sunset"]
        dusk = s["dusk"]

        effects["off"](False)
        
        def compare_time(a,b):
            print(a.hour,a.minute,a.second," - ",b.hour,b.minute,b.second)
            return a.hour < b.hour or (a.hour == b.hour and a.minute < b.minute) or  (a.hour == b.hour and a.minute == b.minute and a.second < b.second) 
        
        if(compare_time(sunset,now) and compare_time(now,dusk)):
            effects["sundown"]()
        elif(dht.humi > 60):
            effects["rain"]()
        elif(tmp.temp > 30):
            effects["steam"]()
        else:
            effects["fade"]()
    

effects = {
    "off":off,
    "solid":solid,
    "rain":rain,
    "sundown":zons_onder,
    "orbit":orbit,
    "sound":sound,
    "rainbow sound":rainbow_sound,
    "steam":steam,
    "fade":fade,
    "automatic":automatic,
    "test":test
}

framerate = 0.01
frames = 0
one_sec = 1 / framerate
j=0

leds.effect = "off"

while True:    
    effects[leds.effect]()
    if((frames % (10 * one_sec)) == 0):
        values = dht.read()
        database.create_dht(get_time(),values["temp"],values["humi"])
        database.create_tmp(get_time(),tmp.temp)
    frames+=1
    sleep(framerate)
