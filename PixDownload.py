import os
import sys
import io
import time
import json
import re
import requests
import random
import ssl
import certifi
import urllib3
import WebTool
import PixTool
from PIL import Image
import codecs
import unicodedata
from collections import OrderedDict

minsim='80!'
EnableRename=False
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
thumbSize = (250,250)

db_bitmask = 8589938016

"""
#enable or disable indexes
index_hmags='0'
index_reserved='0'
index_hcg='0'
index_ddbobjects='0'
index_ddbsamples='0'
index_pixiv='1'
index_pixivhistorical='1'
index_reserved='0'
index_seigaillust='1'
index_danbooru='0'
index_drawr='1'
index_nijie='1'
index_yandere='0'
index_animeop='0'
index_reserved='0'
index_shutterstock='0'
index_fakku='0'
index_hmisc='0'
index_2dmarket='0'
index_medibang='0'
index_anime='0'
index_hanime='0'
index_movies='0'
index_shows='0'
index_gelbooru='0'
index_konachan='0'
index_sankaku='0'
index_animepictures='0'
index_e621='0'
index_idolcomplex='0'
index_bcyillust='0'
index_bcycosplay='0'
index_portalgraphics='0'
index_da='1'
index_pawoo='0'
index_madokami='0'
index_mangadex='0'

#generate appropriate bitmask
db_bitmask = int(index_mangadex+index_madokami+index_pawoo+index_da+index_portalgraphics+index_bcycosplay+index_bcyillust+index_idolcomplex+index_e621+index_animepictures+index_sankaku+index_konachan+index_gelbooru+index_shows+index_movies+index_hanime+index_anime+index_medibang+index_2dmarket+index_hmisc+index_fakku+index_shutterstock+index_reserved+index_animeop+index_yandere+index_nijie+index_drawr+index_danbooru+index_seigaillust+index_anime+index_pixivhistorical+index_pixiv+index_ddbsamples+index_ddbobjects+index_hcg+index_hanime+index_hmags,2)
print("dbmask="+str(db_bitmask))
"""

"""
#encoded print - handle random crap
def printe(line):
    print(str(line).encode(sys.getdefaultencoding(), 'replace')) #ignore or replace
"""

"""
def Read_pictures():
    root = os.getcwd()
    WorkPath = root + "\\Predownload"
    filenames = os.listdir(WorkPath)
    
    pictures = []
    for fname in filenames:
        if fname[-3:] == "jpg" or fname[-3:] == "png":
            faddr = fr"{WorkPath}\{fname}"
            pictures.append((fname,faddr))
    return pictures

class Pixiv_Piclist:
    def __init__(self):
        self.piclist = []
        self.thislist = []

    def WriteList(self, piclist:list):
        self.piclist = piclist
        self.thislist = piclist
        with open("Download_List.json","w+") as file:
            json.dump(self.piclist, file)
            file.close()
    
    def readlist(self, num = 0):
        with open("Download_List.json","r") as file:
            self.piclist = json.load(file)
            file.close()
            this_piclist = self.piclist[num:]
        return this_piclist
    
    def printwholelist(self):
        self.readlist()
        print("已存储%d张图片的信息:" % len(self.piclist))
        for pic in self.piclist:
            print(pic["pic_name"]+" = "+pic["illust_id"])
        print("")
        
    def printthislist(self, num = 0):
        self.thislist = self.readlist(num = num)
        print(f"已下载{num}张图片，剩余{len(self.thislist)}张图片:")
        for pic in self.thislist:
            print(pic["pic_name"]+" = "+pic["illust_id"])
        print("")
"""

def main():
    #ppl = Pixiv_Piclist()
    #WebTool.api_key = input("Enter the SauseNAO api-key: ")
    Mode = input("Choose the download mode:\n1: Direct Mode; 2: Mirror Mode.\n")
    if Mode == "1":
        PP = PixTool.Pixiv_Picture()
        PP.InputTag()
        PP.Download()
        print("File downloaded successfully. Program exiting...")
        time.sleep(5)
    elif Mode == "2":
        PPM = PixTool.Pixiv_Picture_Mirror()
        PPM.InputTag()
        PPM.PicDownload()
        print("File downloaded successfully. Program exiting...")
        time.sleep(5)

if __name__ == "__main__":
    main()
    os.system("pause")
