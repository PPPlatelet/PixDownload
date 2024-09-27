import logging
import sys
import requests
import cv2
import json
import re
import time
import module.WebTool as WebTool
import urllib3

minsim: str = '80!'
db_bitmask: int = 32768

SAUCE_URL: str = "https://saucenao.com/search.php"


def CompressImage(path: str = None, maxsize: int = 512):
    img = cv2.imread(path)

    height, width = img.shape[:2]
    if height >= 10000 or width >= 10000:
        scale = 0.25
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

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


class SauceNAO_Picture:
    def __init__(self, pic_name=None, pic_path=None):
        if pic_path is None:
            pic_path = []
        if pic_name is None:
            pic_name = []
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.pic_name = pic_name
        self.pic_path = pic_path
        self.service_name = []
        self.illust_id = []
        self.result = []

    def PrintSaucePictures(self):
        for element, picname in enumerate(self.pic_name):
            print(
                f"name: {picname}; "
                f"path: {self.pic_path[element]}; "
                f"service_name: {self.service_name[element] if self.service_name[element] != "" else "Default"}; "
                f"illust_id: {self.illust_id[element] if self.illust_id[element] != "" else "Unknown"}; "
                f"result: {self.result[element]}"
            )

    def find_saucenao(self):
        index = 0
        url = (f"{SAUCE_URL}"
               f"?api_key={WebTool.api_key}"
               f"&output_type=2"
               f"&testmode=1"
               f"&dbmaski={db_bitmask}"
               f"&db=10"
               f"&numres=10"
               f"&minsim={minsim}")
        while index < len(self.pic_path):
            picpath = self.pic_path[index]
            # with open(picpath, "rb") as file:
            ImgData = CompressImage(picpath, 1024)
            stream = {'file': ("image.jpg", ImgData)}
            processResults = True
            results = None

            while 1:
                try:
                    response: requests.Response = requests.post(url=url, files=stream, headers=WebTool.SAUCE_HEADERS,
                                                                verify=False)  #True
                except requests.exceptions.SSLError:
                    # print(e)
                    continue
                except requests.exceptions.ConnectTimeout as e:
                    logging.exception(e)
                    exit(1)
                except requests.exceptions.ProxyError as e:
                    logging.exception(e)
                    exit(1)
                if response.status_code != 200:
                    if response.status_code == 403:
                        print("Incorrect or Invalid API Key! Please Edit Script to Configure...")
                        sys.exit(1)
                    # generally non 200 statuses are due to either overloaded servers or the user is out of searches.
                    print(f"Statue code: {str(response.status_code)}")
                    time.sleep(10)
                    continue
                results = json.loads(response.text)
                if int(results["header"]["user_id"]) > 0:
                    # api responded
                    print(f"Remaining Searches 30s|24h: "
                          f"'{str(results['header']['short_remaining'])}'|"
                          f"'{str(results['header']['long_remaining'])}'"
                          )

                    if int(results["header"]["status"]) == 0:
                        # search succeeded for all indexes,results usable.
                        break
                    if int(results["header"]["status"]) > 0:
                        """
                            One or more indexes are having an issue.
                            This search is considered partially successful, even if all indexes failed,
                            so is still counted against your limit.
                            The error may be transient, but because we don't want to waste searches,
                            allow time for recovery.
                        """
                        print("API Error. Retrying in 600 seconds...")
                        time.sleep(600)
                        continue
                    """
                        Problem with search as submitted, bad image, or impossible request.
                        Issue is unclear, so don't flood requests.
                    """
                    print("Bad image or other request error. Skipping in 10 seconds...")
                    processResults = False
                    self.AppendValue()
                    time.sleep(10)
                    index += 1
                    break
                """
                                General issue, api did not respond. Normal site took over for this error state.
                                Issue is unclear, so don't flood requests.
                                """
                processResults = False
                self.AppendValue()
                time.sleep(10)
                index += 1
                break

            if not processResults:
                print("no result... ;_;")
                self.AppendValue()
                index += 1
                continue

            if not int(results["header"]["results_returned"]):
                # none results
                print("missing...")
                self.AppendValue()
                index += 1
                continue

            # one or more results were returned
            result: list = [
                res
                for element, res in enumerate(results["results"])
                if (
                    float(results['results'][element]['header']['similarity']) >
                    float(results['header']['minimum_similarity'])
                )
            ]
            result = self.SimilarityQuickSort(result)[::-1]

            if not result:
                print("missing...")
                self.AppendValue()
                index += 1
                continue

            print("Possible respond:")
            for element, value in enumerate(result):
                print(f"{element + 1}. similarity: {value["header"]["similarity"]}")

                # get vars to use
                index_id = value["header"]["index_id"]

                if index_id in [5, 6]:
                    # 5->pixiv 6->pixiv historical
                    service_name = 'pixiv'
                    illust_id = value['data']['pixiv_id']
                    if str(illust_id) in self.illust_id:
                        print("Picture repeat recognition! Pulling the next one...")
                        self.AppendValue(service_name, illust_id, False)
                        index += 1
                        break
                    self.AppendValue(service_name, illust_id, True)
                    index += 1
                    break
                try:
                    if "pixiv" in value['data']['source'] or "pximg" in value['data']['source']:
                        illust_id = re.findall(r'\d+$', value['data']['source'])[-1]
                        if str(illust_id) in self.illust_id:
                            print("Picture repeat recognition! Pulling the next one...")
                            self.AppendValue("pixiv", str(illust_id), False)
                            index += 1
                            break
                        self.AppendValue("pixiv", str(illust_id), True)
                        index += 1
                        break
                    if element == len(result) - 1:
                        self.AppendValue()
                        index += 1
                        break
                except:
                    if element == len(result) - 1:
                        self.AppendValue()
                        index += 1
                        break

            if int(results['header']['long_remaining']) < 1:
                print("Out of searches for today. Sleeping for 6 hours...")
                time.sleep(6 * 60 * 60)

            if int(results["header"]["short_remaining"]) < 1:
                print("Out of searches for this 30 second period. Sleeping for 25 seconds...")
                time.sleep(25)

        print("All Done!")

    def AppendValue(self, service_name: str = "", illust_id: str = "", result: bool = False):
        self.service_name.append(service_name)
        self.illust_id.append(str(illust_id))
        self.result.append(result)

    def SimilarityQuickSort(self, arr: list):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if float(x["header"]["similarity"]) < float(pivot["header"]["similarity"])]
        middle = [x for x in arr if float(x["header"]["similarity"]) == float(pivot["header"]["similarity"])]
        right = [x for x in arr if float(x["header"]["similarity"]) > float(pivot["header"]["similarity"])]
        # print(f"{left}\n{middle}\n{right}")
        return self.SimilarityQuickSort(left) + middle + self.SimilarityQuickSort(right)

    def FindDelList(self):
        filepath: list = []
        filename: list = []
        illust_id: list = []
        for element, path in enumerate(self.pic_path):
            if self.result[element]:
                filepath.append(path)
                filename.append(self.pic_name[element])
                illust_id.append(self.illust_id[element])
                continue
            if self.illust_id[element] in illust_id:
                filepath.append(path)
                filename.append(self.pic_name[element])
        return filepath, filename
