import urllib.request
from bs4 import BeautifulSoup
import re
import os
import sys
import sqlite3
import datetime

def download_web_image(url,folder_name,file_name):
    print("url = " , url)
    #full_name = "./"+foldername + "/"+str(indexnum)+".jpg"
    full_name = "/Users/vichy/DCInside/mina/" + folder_name + "/" + file_name #161110

    try:
        urllib.request.urlretrieve(url,full_name)
    except:
        with open('errmina.txt', 'a') as mysavedata:
            print("===Error in DownImg===" , file=mysavedata)
            print("Folder: " + folder_name, file=mysavedata)
            print("URL: " + url, file=mysavedata)


def ensure_dir(folderName):
    #d = os.path.dirname(f)
    #d = os.path.abspath(f)
    try:
        dirpath = os.path.join('/Users/vichy/DCInside/mina/', folderName) #161110

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            print(dirpath + "folder made")
            return 0
        else:
            print(dirpath + "failed in making folder")
            return 1

    except:
        with open('errmina.txt', 'a') as mysavedata:
            print("===Error in MakingFolder===" ,file=mysavedata)
            print("Foldername: " + dirpath, file=mysavedata)


def goIntoUrl(url_info):
    req = urllib.request.Request(url_info);  # going in article
    data = urllib.request.urlopen(req).read()
    bs2 = BeautifulSoup(data, 'html.parser')
    return bs2


class DB:
    "SQLITE3 wrapper class"
    def __init__(self):
        self.conn = sqlite3.connect('./DCcrawlerDB')
        self.cursor = self.conn.cursor()
        self.conn.isolation_level = None
        self.cursor.execute('CREATE TABLE IF NOT EXISTS urls(url text, state int)')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS IDX001 ON urls(url)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS IDX002 ON urls(state)')

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def insertURL(self, url, state=0):
        try:
            self.cursor.execute("INSERT INTO urls VALUES ('%s',%d)" % (url, state))
        except:
            return 0
        else:
            return 1

    def selectUncrawledURL(self):
        self.cursor.execute('SELECT * FROM urls where state=0')
        return [ row[0] for row in self.cursor.fetchall()]

    def updateURL(self,url,state=1):
        self.cursor.execute("UPDATE urls SET state=%d WHERE url='%s'"%(state,url))

    def isCrawledURL(self,url):
        self.cursor.execute("SELECT COUNT(*) FROM urls WHERE url='%s' and state=1"%url)
        ret = self.cursor.fetchone()
        return ret[0]



if __name__ == "__main__":
    with open('errmina.txt', 'w') as mysavedata: #initiate err text file
        print("==Empty==", file=mysavedata)
    db = DB()
    pageindex = 1
    pageURL = "http://gall.dcinside.com/mgallery/board/lists/?id=twicemina&page=1&exception_mode=recommend"  # recommended Article

    while (pageindex < 20):  # navigate to X Page
        req = urllib.request.Request(pageURL);
        data = urllib.request.urlopen(req).read()
        bs = BeautifulSoup(data, 'html.parser')

        eachATag = bs.find_all('a')

        index = 0
        fileName = ''


        for tempData in eachATag: #
            try:
                prop = tempData.get('class')  # get class property
                #print(tempData)
                if prop != None and (prop[0] == "f_l"):  #if end of this page
                    pageindex += 1 #go to next page
                    pageURL = "http://gall.dcinside.com/mgallery/board/lists/?id=twicemina&page=" + str(pageindex) + "&exception_mode=recommend"
                    print("next page is = ", pageindex)
                    break #end of for and go to while loop
                #end of if
                class_list = ['icon_pic_b', 'icon_movie', 'icon_txt_b']
                if prop != None and prop[0] in class_list:  # if class property exist, check icon_pic_n
                    url_info = tempData.get('href') #get Article URL
                    if url_info[:4] != "http": #attach http://
                        url_info = "http://gall.dcinside.com" + url_info
                    #end of if

                    temp_url = url_info.partition("&page")
                    url_info = temp_url[0]
                    #print("%s : %s" % (url_info, tempData.get_text()))


                    if db.isCrawledURL(url_info) != 0:#if this page is Crawled already
                        print('already crawled')
                        continue
                    returnvalue = db.insertURL(url_info)
                    print("%s : %s is inserted" % (url_info, tempData.get_text()))
                    db.updateURL(url_info)

                    returnvalue = 0
                    folder_name = tempData.get_text()
                    returnvalue = ensure_dir(folder_name)  # makeDir
                    if returnvalue == 1:
                        print('dir 생성실패')
                        sys.exit(1)
                    bs2 = goIntoUrl(url_info)
                    parsedData = bs2.find_all('div', 's_write')
                    #parsedData = bs2.find_all('ul', 'appending_file')
                    #parsedData = bs2.find_all('ul', 'appending_file')#finding on AppendingFile
                    parsedData2 = parsedData[0].find_all('img')
                    for index2, tempInFor in enumerate(parsedData2):
                        filename = ''
                        tempInIf = tempInFor.get('onclick')
                        if tempInIf:
                            tempurl = re.split('[\']', tempInIf)
                            tempurl = tempurl[1]
                            tempurl = tempurl.replace("Pop", "", 1)
                            tempurl = tempurl.replace("dcimg1", "dcimg2", 1)
                            filename = str(index2) + '.jpg'


                        else:
                            tempurl = tempInFor.get('src')
                            tempurl = tempurl.replace("dcimg1", "dcimg2", 1)
                            filename = str(index2) + '.gif'

                        download_web_image(tempurl, folder_name, filename)


            except:
                with open('errmina.txt', 'a') as mysavedata:
                    print("===Error in Crawling===", file=mysavedata)













