import urllib3
import WebTool
import requests
import time
import re
import os
import json

class Pixiv_Picture:
    def __init__(self, net:str = None, pid:list = None):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.net = net
        self.pid = pid if pid is not None else []
        self.name = [f"{p}.jpg" for p in self.pid]
        self.url = [f"{net}{p}"for p in self.pid]
        self.picurls = []
        self.headers = WebTool.MY_HEADERS

    def Download(self):
        self.GetUrl()
        self.PicDownload()

    def GetUrl(self):
        for element,url in enumerate(self.url):
            while 1:
                try:
                    response = requests.get(url = url, headers = self.headers, verify=False)
                    if response.status_code == 200:
                        print(f"Picture {self.pid[element]} had been found. ")
                        break
                    elif response.status_code == 404:
                        print("Web not found! Getting the another one...")
                        break
                    else:
                        print("Unknown error! Please check the network. ")
                        break
                except:
                    print("Connection failed! Retrying...")
                    time.sleep(5)
                    continue
            
            retxt = re.compile(r"img.{16,30}%s.{0,20}\.jpg" %self.pid[element])
            temp = retxt.findall(response.text)
            time_text = re.search(r"/\d{4}/\d{2}/\d{2}/\d{2}/\d{2}/\d{2}/",temp[0])
            self.picurls.append(f"https://i.pximg.net/img-original/img{time_text[0]}{self.pid[element]}_p0.jpg")
    
    def PicDownload(self):
        for element,url in enumerate(self.picurls):
            pic_type = url[-3:]
            if pic_type == "png" or pic_type == "jpg":
                index = 0
                while 1:
                    try:
                        pic = requests.get(url = f"{url[:-5]}{index}.{pic_type}", headers = self.headers, verify = False)
                        if pic.status_code == 200:
                            self.SaveFile(pic = pic, element = element, index = index, pic_type = pic_type)
                            index += 1
                        elif pic.status_code == 404:
                            print("A set of pictures downloaded successfully.")
                            break
                        else:
                            print("Unknown error! Please check the network")
                            break
                    except:
                        print("Connection failed! Retrying...")
                        time.sleep(5)
                        continue

    def SaveFile(self, pic:requests.Response = None, element:int = None, index:int = None, pic_type:str = None):
        if pic is not None and not isinstance(pic, requests.Response):
            raise TypeError("pic must be a requests.Response object")
        if element is not None and not isinstance(element, int):
            raise TypeError("element must be an integer")
        if index is not None and not isinstance(index, int):
            raise TypeError("index must be an integer")
        if pic_type is not None and not isinstance(pic_type, str):
            raise TypeError("pic_type must be a string")
        
        os.makedirs(f"pixiv/{self.pid[element]}",exist_ok=True)
        filename = f"{self.pid[element]}_p{index}.{pic_type}"
        with open(f"pixiv/{self.pid[element]}/{filename}", "wb") as file:
            file.write(pic.content)
            print(f"File '{filename}' downloaded successfully. ")

class Pixiv_Picture_Mirror(Pixiv_Picture):
    def __init__(self, net:str = None, pid:list = None):
        super().__init__(net = net, pid = pid)

    def Download(self):
        self.PicDownload()

    def PicDownload(self):
        for element,url in enumerate(self.url):
            pic_type = self.name[element][-3:]
            if pic_type == "png" or pic_type == "jpg":
                index = 0
                while 1:
                    try:
                        pic = requests.get(url = f"{url}-{index+1}.{pic_type}", headers = self.headers, verify = False)
                        if pic.status_code == 200:
                            self.SaveFile(pic = pic, element = element, index = index, pic_type = pic_type)
                            index += 1
                        elif pic.status_code == 404:
                            if index > 0:
                                print("A set of pictures downloaded successfully.")
                                break
                            else:
                                pic = requests.get(url = f"{url}.{pic_type}", headers=self.headers, verify=False)
                                if pic.status_code == 200:
                                    self.SaveFile(pic = pic, element = element, index = index, pic_type = pic_type)
                                    break
                                elif pic.status_code == 404:
                                    print("File not found! Please input the correct tag! ")
                                    break
                                else:
                                    print("Unknown error! Please check the network. ")
                                    break
                        else:
                            print("Unknown error! Please check the network. ")
                            break
                    except:
                        print("Connection failed! Retrying...")
                        time.sleep(5)
                        continue

"""
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