#!/usr/bin/env python -u
#This script requires Python 3+, Requests, and Pillow, a modern fork of PIL, the Python Imaging Library: 'easy_install Pillow' and 'easy_install requests'
#For Windows easy_install setup, download and run: https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
#After Installation of easy_install, it will be located in the python scripts directory.

#This is a basic, likley broken example of how to use the very beta saucenao API...
#There are several signifigant holes in the api, and in the way in which the site responds and reports error conditions.
#These holes will likley be filled at some point in the future, and it may impact the status checks used below.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
#################CONFIG##################


##############END CONFIG#################
import sys
#import os
import io
#import unicodedata
import requests
from PIL import Image
import cv2
import json
import codecs
import re
import time
#from collections import OrderedDict
import WebTool
import urllib3
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

api_key = WebTool.api_key
EnableRename=False
minsim='80!'#forcing minsim to 80 is generally safe for complex images, but may miss some edge cases. If images being checked are primarily low detail, such as simple sketches on white paper, increase this to cut down on false positives.
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
#encoded print - handle random crap
def printe(line):
    print(str(line).encode(sys.getdefaultencoding(), 'replace')) #ignore or replace
"""

class SauceNAO_Picture:
        def __init__(self, pic_name : list = [], pic_path : list = []):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.pic_name = pic_name
            self.pic_path = pic_path
            self.service_name = []
            self.member_id = []
            self.illust_id = []
            self.result = []

        def print_saucenao_picture(self):
            for element,picname in enumerate(self.pic_name):
                print(
                    f"name: {picname}; "
                    f"path: {self.pic_path[element]}; "
                    f"service_name: {self.service_name[element] if self.service_name[element] is not "" else "default"}; "
                    f"member_id: {self.member_id[element] if self.member_id[element] is not "" else "None"}; "
                    f"illust_id: {self.illust_id[element] if self.illust_id[element] is not "" else "None"}; "
                    f"result: {self.result[element]}"
                )

        def compressimage(self,path:str = None, maxsize:int = 1024):
            img = cv2.imread(path)
            encodeparam = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            success, imgencode = cv2.imencode(".jpg", img, encodeparam)
            ImgData = imgencode.tobytes()
            if len(ImgData) <= maxsize * 1024:
                return ImgData
            
            while len(ImgData) > maxsize * 1024:
                encodeparam[1] -= 5
                if encodeparam[1] <= 10:
                    break

                success, imgencode = cv2.imencode(".jpg", img, encodeparam)
                ImgData = imgencode.tobytes()

            return ImgData


        def find_saucenao(self):
            index = 0
            while index < len(self.pic_path):
                picpath = self.pic_path[index]
                #with open(picpath, "rb") as file:
                ImgData = self.compressimage(picpath, 1024)

                url = 'http://saucenao.com/search.php?output_type=2&numres=1&minsim='+minsim+'&dbmask='+str(db_bitmask)+'&api_key='+WebTool.api_key
                stream = {'file': ("image.jpg", ImgData)}

                processResults = True
                while 1:
                    response = requests.post(url=url,files=stream,headers=WebTool.SAUCE_HEADERS,verify=False)
                    if response.status_code != 200:
                        if response.status_code == 403:
                            print("Incorrect or Invalid API Key! Please Edit Script to Configure...")
                            sys.exit(1)
                        else:
                            #generally non 200 statuses are due to either overloaded servers or the user is out of searches.
                            print(f"Statue code: {str(response.status_code)}")
                            time.sleep(10)
                            continue
                    else:
                        results = json.loads(response.text)
                        if int(results["header"]["user_id"]) > 0:
                            #api responded
                            print(f"Remaining Searches 30s|24h: "
                                f"'{str(results['header']['short_remaining'])}'|"
                                f"'{str(results['header']['long_remaining'])}'"
                            )

                            if int(results["header"]["status"]) == 0:
                                #search succeeded for all indexes,results usable.
                                break
                            else:
                                if int(results["header"]["status"]) > 0:
                                    """
                                    One or more indexes are having an issue.
                                    This search is considered partially successful, even if all indexes failed, so is still counted against your limit.
                                    The error may be transient, but because we don't want to waste searches, allow time for recovery.
                                    """
                                    print("API Error. Retrying in 600 seconds...")
                                    time.sleep(6)
                                    continue
                                else:
                                    """
                                    Problem with search as submitted, bad image, or impossible request.
                                    Issue is unclear, so don't flood requests.
                                    """
                                    print("Bad image or other request error. Skipping in 10 seconds...")
                                    processResults = False
                                    self.service_name.append("")
                                    self.member_id.append("")
                                    self.illust_id.append("")
                                    self.result.append(False)
                                    time.sleep(10)
                                    index += 1
                                    break
                        else:
                            """
                            General issue, api did not respond. Normal site took over for this error state.
                            Issue is unclear, so don't flood requests.
                            """
                            processResults = False
                            self.service_name.append("")
                            self.member_id.append("")
                            self.illust_id.append("")
                            self.result.append(False)
                            time.sleep(10)
                            index += 1
                            break
                
                if processResults:
                    #print(results)

                    if int(results["header"]["results_returned"]) > 0:
                            #one or more results were returned
                        if float(results['results'][0]['header']['similarity']) > float(results['header']['minimum_similarity']):
                            print(f"hit! {str(results["results"][0]["header"]["similarity"])}")

                            #get vars to use
                            service_name = ""
                            illust_id = 0
                            member_id = -1
                            index_id = results["results"][0]["header"]["index_id"]

                            if index_id == 5 or index_id == 6:
                                #5->pixiv 6->pixiv historical
                                service_name='pixiv'
                                member_id = results['results'][0]['data']['member_id']
                                illust_id=results['results'][0]['data']['pixiv_id']
                            elif index_id == 8:
                                #8->nico nico seiga
                                service_name='seiga'
                                member_id = results['results'][0]['data']['member_id']
                                illust_id=results['results'][0]['data']['seiga_id']
                            elif index_id == 10:
                                #10->drawr
                                service_name='drawr'
                                member_id = results['results'][0]['data']['member_id']
                                illust_id=results['results'][0]['data']['drawr_id']								
                            elif index_id == 11:
                                #11->nijie
                                service_name='nijie'
                                member_id = results['results'][0]['data']['member_id']
                                illust_id=results['results'][0]['data']['nijie_id']
                            elif index_id == 34:
                                #34->da
                                service_name='da'
                                illust_id=results['results'][0]['data']['da_id']
                            else:
                                #unknown
                                print('Unhandled Index! Exiting...')
                                sys.exit(2)

                            if str(illust_id) in self.illust_id:
                                print("Picture repeat recognition! Pulling the next one...")
                                self.service_name.append("")
                                self.member_id.append("")
                                self.illust_id.append("")
                                self.result.append(False)
                                index +=1
                                continue

                            try:
                                self.service_name.append(service_name)
                                self.member_id.append(str(member_id))
                                self.illust_id.append(str(illust_id))
                                self.result.append(True)
                                index += 1
                            except Exception as e:
                                print(e)
                                sys.exit(3)

                        else:
                            print(f"miss... {str(results['results'][0]['header']['similarity'])}")
                            self.service_name.append("")
                            self.member_id.append("")
                            self.illust_id.append("")
                            self.result.append(False)
                            index += 1

                    else:
                        print("no result... ;_;")
                        self.service_name.append("")
                        self.member_id.append("")
                        self.illust_id.append("")
                        self.result.append(False)
                        index += 1
                        
                    if int(results['header']['long_remaining']) < 1:
                        print("Out of searches for today. Sleeping for 6 hours...")
                        time.sleep(6*60*60)

                    if int(results["header"]["short_remaining"]) < 1:
                        print("Out of searches for this 30 second period. Sleeping for 25 seconds...")
                        time.sleep(25)
            
            print("All Done!")