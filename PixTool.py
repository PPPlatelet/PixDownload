import urllib3
import WebTool
import requests
import time
import re
import os

class Pixiv_Picture:
    def __init__(self, net:str = None):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.net = net
        self.name = []
        self.pid = []
        self.url = []
        self.picurls = []
        self.headers = WebTool.MY_HEADERS

    def Download(self):
        self.GetUrl()
        self.PicDownload()

    def InputTag(self):
        print("Enter the 'Q' or 'q' to end the input.")
        temp = input("Enter the pixiv tag: ")
        while 1:
            if temp == 'Q' or temp == 'q':
                break
            else:
                try:
                    if int(temp) > 0:
                        self.pid.append(temp)
                        self.name.append(f"{temp}.jpg")
                        self.url.append(f"{self.net}{temp}")
                        temp = input("Input success! Please enter the another pixiv tag: ")
                        continue
                    else:
                        temp = input("Invalid number! Please enter the correct one: ")
                        continue
                except ValueError:
                    temp = input("Unknown error! Please enter the correct one: ")
                    continue

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
    def __init__(self, net:str = None):
        super().__init__(net = net)

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