
import os
from subprocess import check_output
from time import time

def reset_serial():
    os.system("tput reset > /dev/serial0")

def read_ips():
    raw_ips = check_output(["hostname","--all-ip-addresses"]).decode()
    ips = raw_ips.replace(" \n","").split(" ")
    return ips

def image2D(im):
    buf = []
    pix_val = list(im.getdata())
    for i in range(0,im.height):
        buf.append([])
        for j in range(0,im.width):
            c = 0
            try:
                c = pix_val[int(i*im.width + j)][0]
            except:
                c = pix_val[int(i*im.width + j)]
            if(c != 0):
                c = 1
            buf[i].append(c)
    return buf

def get_time():
    return round(time()*1000)

def check_string(string):
    allowed_chars = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 :")
    matched_list = [characters in allowed_chars for characters in string]
    return sum(matched_list) == len(matched_list)