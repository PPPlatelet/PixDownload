import urllib3
import requests
from requests import RequestException, HTTPError
import time
import re
import os
from tqdm import tqdm

from module.util import Timer
from WebTool import PIXIV_HEADERS, DirOK
from module.logger import logger

class PixivPicture:
    def __init__(self, net: str = None, pid: list = None):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.net = net
        self.pid = pid if pid is not None else []
        self.name = [f"{p}.jpg" for p in self.pid]
        self.url = [f"{net}{p}" for p in self.pid]
        self.picurls = []
        self.headers = PIXIV_HEADERS

    def download(self):
        self.get_url()
        self.pic_download()

    def get_url(self):
        for element, url in enumerate(self.url):
            response = None
            failed = 0
            timer = Timer(3).start()
            while failed < 10:
                try:
                    response = requests.get(url=url, headers=self.headers, verify=False)
                    response.raise_for_status()
                    logger.info(f"Picture {self.pid[element]} has been found.")
                    break
                except HTTPError:
                    if response is not None and response.status_code == 404:
                        logger.warning("Web not found! Trying another one...")
                        break
                    else:
                        logger.warning("Connection failed! Retrying...")
                        failed += 1
                        timer.wait()
                        timer.reset()
                except RequestException:
                    logger.warning("Connection failed! Retrying...")
                    failed += 1
                    timer.wait()
                    timer.reset()

            if response is not None:
                self.parse_pic_url(response.text, element)

    def parse_pic_url(self, text: str, element: int):
        retxt = re.compile(fr"img.{16,30}{self.pid[element]}.{0,20}\.jpg")
        temp = retxt.findall(text)
        time_text = re.search(r"/\d{4}/\d{2}/\d{2}/\d{2}/\d{2}/\d{2}/", temp[0])
        self.picurls.append(f"https://i.pximg.net/img-original/img{time_text[0]}{self.pid[element]}_p0.jpg")

    def pic_download(self):
        for element, url in enumerate(self.picurls):
            pic_type = url[-3:]
            if pic_type not in ("png", "jpg"):
                continue

            pic = None
            index = 0
            while True:
                try:
                    pic = requests.get(url=f"{url[:-5]}{index}.{pic_type}", headers=self.headers, verify=False)
                    pic.raise_for_status()
                    self.save_file(pic=pic, element=element, index=index, pic_type=pic_type)
                    index += 1
                except HTTPError:
                    if pic is not None and pic.status_code == 404:
                        logger.info("A set of pictures downloaded successfully.")
                        break
                    else:
                        logger.error("Unknown error! Please check the network")
                        break
                except RequestException:
                    logger.warning("Connection failed! Retrying...")
                    time.sleep(5)

    def save_file(self, pic: requests.Response, element: int, index: int, pic_type: str,
                 total: int = None):
        targetpath = os.path.join('pixiv', self.pid[element])
        os.makedirs(targetpath, exist_ok=True)
        filename = f"{self.pid[element]}_p{index}.{pic_type}"
        with (
            open(f"{targetpath}/{filename}", "wb") as file,
            tqdm(desc=filename, total=total, unit='iB', unit_scale=True, unit_divisor=1024) as bar
        ):
            for content in pic.iter_content(chunk_size=1024):
                size = file.write(content)
                bar.update(size)
        logger.info(f"File '{filename}' downloaded successfully. ")


class PixivPictureMirror(PixivPicture):
    def __init__(self, net: str = None, pid: list = None):
        super().__init__(net=net, pid=pid)

    def download(self):
        self.pic_download()

    def pic_download(self):
        for element, url in enumerate(self.url):
            pic_type = self.name[element][-3:]

            if pic_type not in ("png", "jpg"):
                continue
            flag = False
            index = 0
            while not flag:
                try:
                    pic = requests.get(url=f"{url}-{index + 1}.{pic_type}", headers=self.headers, verify=False,
                                       stream=True)
                except requests.exceptions.SSLError:
                    # print(e)
                    continue
                if pic.status_code == 200:
                    total = int(pic.headers.get('content-length', 0))
                    self.SaveFile(pic=pic, element=element, index=index, pic_type=pic_type, total=total)
                    index += 1
                    continue
                if pic.status_code == 404:
                    if index > 0:
                        print("A set of pictures downloaded successfully. ")
                        break
                    while not Flag:
                        try:
                            pic = requests.get(url=f"{url}.{pic_type}", headers=self.headers, verify=False)
                        except requests.exceptions.SSLError:
                            # print(e)
                            continue
                        if pic.status_code == 200:
                            total = int(pic.headers.get('content-length', 0))
                            self.SaveFile(pic=pic, element=element, index=index, pic_type=pic_type, total=total)
                            Flag = True
                        elif pic.status_code == 404:
                            print("File not found! Please input the correct tag! ")
                            Flag = True
                        else:
                            print("Unknown error! Please check the network. ")
                            Flag = True
                else:
                    print("Unknown error! Please check the network. ")
                    break


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
