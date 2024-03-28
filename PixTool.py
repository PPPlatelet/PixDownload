import urllib3
import WebTool
import requests
import time
import re
import os

class Pixiv_Picture:
    def __init__(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.name = []
        self.pid = []
        self.url = []
        self.picurls = []
        self.r = None
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
                        self.pid.append(temp),self.name.append(f"{temp}.jpg"),self.url.append(f"https://www.pixiv.net/artworks/{temp}")
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
                    self.r = requests.get(url = url, headers = self.headers, verify=False)
                    break
                except:
                    print("Connection failed! Retrying...")
                    time.sleep(5)
                    continue
            
            temp = re.findall("https://i.pximg.net/img-original/img/[^\"]*",self.r.text)
            retxt = re.compile(r"img.{16,30}%s.{0,20}\.jpg" %self.pid[element])
            temp = retxt.findall(self.r.text)
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
                            os.makedirs(f"pixiv/{self.pid[element]}",exist_ok=True)
                            filename = f"{self.pid[element]}_p{index}.{pic_type}"
                            with open(f"pixiv/{self.pid[element]}/{filename}", "wb") as file:
                                file.write(pic.content)
                                print(f"File '{filename}' downloaded successfully.")
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