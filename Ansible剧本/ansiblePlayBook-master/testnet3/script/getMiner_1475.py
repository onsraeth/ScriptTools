import requests
import shutil
import datetime
import time
import hashlib
import json
import threading

def getWallet(fileName):
    import os
    walletList = []
    cmd = """ cat %s | awk '{print $1}' """%(fileName)
    walletList = os.popen(cmd).read().rstrip().split("\n")
    return walletList

def sendRequest(idx):
    dic = ip_list[idx]
    wallet = wallet_list[int(idx/2)]
    ip = dic["ip"]
    port = dic["port"]
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Start thread ",idx," using IP: ",ip,", PORT: ",port)
    proxyUrl = "http://" + ip + ":" + str(port)
    proxy = {'http': proxyUrl,"https": proxyUrl}
    params = {"address":wallet,"sectorSize":sectorSize}
    #print(wallet)
    try:
        r1 = requests.get(fountain_url,params=params,proxies=proxy)
        if("200"==str(r1.status_code)):
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " res1 status code : " + str(r1.status_code))
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " res1 status code : " + str(r1.status_code) + ". Response msg: " + r1.text)
    except requests.exceptions.ConnectTimeout:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " Connect Timeout!!! Try again..." + ". Response msg: ")
        time.sleep(0.2)
        r2 = requests.get(fountain_url,params=params,proxies=proxy)
        if("200"==str(r2.status_code)):
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " res2 status code : " + str(r2.status_code))
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " res2 status code : " + str(r2.status_code) + ". Response msg: " + r2.text)
    except requests.exceptions.ConnectionError:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " Connection Error!!! Try again..." + ". Response msg: ")
        time.sleep(0.2)
        r3 = requests.get(fountain_url,params=params,proxies=proxy)
        if("200"==str(r3.status_code)):
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " res3 status code : " + str(r3.status_code))
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " res3 status code : " + str(r3.status_code) + ". Response msg: " + r3.text)
    except requests.packages.urllib3.exceptions.MaxRetryError:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " MaxRetry Error!!! Stop thread...")
    except requests.exceptions.ProxyError:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " Proxy Error!!! Stop thread...")
    except Exception:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Thread " + str(idx) + " Unknown Error!!! Stop thread...")

if __name__ == '__main__':
    ###???????????????
    orderId = "O20040317033276055556"
    secret = "4741801e439c96bc4163e1aca6def39f"
    #############################################################################################
    ################ ???1475,?????????475*(2/3)?????????(=??????IP?????????)?????????475*(1/3)???wallet??????
    ################ ??????IP??????????????????wallet?????????2???,????????????wallet?????????2???mkminer???????????????2???IP
    num = 190 #????????????200
    #sectorSize = 34359738368
    sectorSize = 536870912
    fountain_url="http://http://39.170.24.100:39292/mkminer"
    #############################################################################################

    pid = "-1"
    cid = "-1"
    unbindTime = "180" ### ip????????????,????????????,3min?????????????????????IP
    noDuplicate = "1"
    lineSeparator = "0"
    singleIp = "0"
    timeNow = str(int(time.time())) #?????????
    # ??????sign
    txt = "orderId=" + orderId + "&secret=" + secret + "&time=" + timeNow
    sign = hashlib.md5(txt.encode()).hexdigest()
    # ??????URL??????200???IP
    url = "http://api.ipproxy.info:8422/api/getIp?type=1&num=" + str(num) + "&pid=" + pid + "&unbindTime=" + unbindTime + "&cid=" + cid +  "&orderId=" + orderId + "&time=" + timeNow + "&sign=" + sign + "&dataType=0&lineSeparator=" + lineSeparator + "&noDuplicate=" + noDuplicate + "&singleIp=" + singleIp
    res1 = requests.get(url).content
    #print(res1)
    js_res = json.loads(res1)
    ip_list = js_res["data"]
    # ????????????URL??????200???IP
    res2 = requests.get(url).content
    js_res = json.loads(res2)
    ip_list += js_res["data"]
    #print(ip_list)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Get IP number: ",len(ip_list))

    wallet_list = getWallet("./wallet_key.txt")
    threads=[]
    for i in range(0,len(ip_list)):
        t=threading.Thread(target=sendRequest,args=(i,))
        threads.append(t)
    for t in threads:
        t.start()
        time.sleep(0.3)
    for t in threads:
        t.join()