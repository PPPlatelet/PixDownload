import os
import sys
#import io
import time
#import json
#import re
#import requests
#import random
#import ssl
#import certifi
#import urllib3
import WebTool
import PixTool
import SauceTool
#from PIL import Image
#import codecs
#import unicodedata
#from collections import OrderedDict

DirectURL = "https://www.pixiv.net/artworks"
MirrorURL = "https://pixiv.nl/"

def Read_pictures():
    WorkPath = f"{os.getcwd()}\\Predownload"
    filenames = os.listdir(WorkPath)
    picname = []
    picpath = []
    for fname in filenames:
        if fname.endswith(".jpg") or fname.endswith(".png") or fname.endswith(".jpeg") or fname.endswith(".bmp"):
            fpath = f"{WorkPath}\\{fname}"
            picname.append(fname)
            picpath.append(fpath)
    return picname,picpath

def main():
    #PPL = PixTool.Pixiv_Piclist()
    WebTool.api_key = "0da33028dcf5b66e35741e714fbaa3e0ccedc0eb"#input("Enter your SauseNAO api-key: ")
    num = input("Press the download mode: 1.Auto mode 2.Hand ctrl mode 0.Exit\n")
    Mode = input("Choose the download mode:\n1: Direct Mode; 2: Mirror Mode.\n")
    if num == "1":
        picname, picpath = Read_pictures()
        SP = SauceTool.SauceNAO_Picture(picname,picpath)
        SP.find_saucenao()
        SP.print_saucenao_picture()
        pid = []
        for element,illustid in enumerate(SP.illust_id):
            if SP.service_name[element] =="pixiv":
                pid.append(illustid)
        if Mode == "1":
            PP = PixTool.Pixiv_Picture(net = DirectURL, pid = pid)
            PP.Download()
            print("File downloaded successfully. Program exiting...")
            time.sleep(5)
        elif Mode == "2":
            PPM = PixTool.Pixiv_Picture_Mirror(net = MirrorURL, pid = pid)
            PPM.Download()
            print("File downloaded successfully. Program exiting...")
            time.sleep(5)
    elif num == "2":
        print()
        filename = []
        filepath = []
        pixtag = []
        temp = input("Input the file name or the pixiv tag.")
        while 1:
            if temp == "Q" or temp == "q":
                break
            else:
                if (temp.endswith(".jpg") or 
                    temp.endswith(".png") or 
                    temp.endswith(".jpeg") or 
                    temp.endswith(".bmp")) and os.path.exists(f"{os.getcwd()}\\{temp}"):
                    filename.append(temp)
                    filepath.append(f"{os.getcwd()}\\{temp}")
                    temp = input("Input success! Please enter again: ")
                    continue
                try:
                    if int(temp) > 0:
                        pixtag.append(temp)
                        temp = input("Input success! Please enter again: ")
                        continue
                    else:
                        temp = input("Invalid number! Please enter the correct one: ")
                        continue
                except ValueError:
                    temp = input("Invalid number! Please enter the correct one: ")
                    continue
        
        SP = SauceTool.SauceNAO_Picture(filename,filepath)
        SP.find_saucenao()
        SP.print_saucenao_picture()
        pid = []
        for element,illustid in enumerate(SP.illust_id):
            if SP.service_name[element] =="pixiv":
                pid.append(illustid)
        pid.extend(pixtag)
        if Mode == "1":
            PP = PixTool.Pixiv_Picture(net = DirectURL, pid = pid)
            PP.Download()
            print("File downloaded successfully. Program exiting...")
            time.sleep(5)
        elif Mode == "2":
            PPM = PixTool.Pixiv_Picture_Mirror(net = MirrorURL, pid = pid)
            PPM.Download()
            print("File downloaded successfully. Program exiting...")
            time.sleep(5)
    else:
        print("See you next time.")
        time.sleep(5)
        sys.exit()

if __name__ == "__main__":
    main()
    os.system("pause")
