import sys
import urllib2
import urllib
import ssl
import threading
import time
import os
import httplib
from random import randint
from Utils import *
from HTMLParser import HTMLParser
NastolRootURL="http://www.nastol.com.ua"

class NastolWallpaperInfoPageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.sourceURL=""
        self.inOrig=False

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            #LogD("START_TAG :", tag,"attrs = ",attrs)
            clas = getAttrByKey("class",attrs)
            if clas == "orig":
                self.inOrig = True
        elif tag == "a" and self.inOrig == True:
            self.sourceURL = getAttrByKey("href",attrs)
            self.inOrig=False

class NastolCatalogPageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.ListImageURL=[]

    def handle_starttag(self, tag, attrs):
        LogD("handle_starttag :", tag," attrs = ",attrs)
        if tag == "a":
            #LogD("a tag entering:" , "AND ATTRS = ",attrs)
            cl = getAttrByKey("class",attrs)
            if cl == "screen-link":
                href = getAttrByKey("href",attrs)
                if href != None:
                    LogD("Found Image URL : ", href)
                    self.ListImageURL.append(href)
    def handle_endtag(self, tag):
        LogD("handle_endtag :", tag)

    # Overridable -- handle character reference
    def handle_charref(self, name):
        LogD("handle_charref :", name)

    # Overridable -- handle entity reference
    def handle_entityref(self, name):
        LogD("handle_entityref :", name)

    # Overridable -- handle data
    def handle_data(self, data):
        LogD("handle_data :", data)

    # Overridable -- handle comment
    def handle_comment(self, data):
        LogD("handle_comment :", data)

    # Overridable -- handle declaration
    def handle_decl(self, decl):
        LogD("handle_decl :", decl)

    # Overridable -- handle processing instruction
    def handle_pi(self, data):
        LogD("handle_pi :", data)

    def unknown_decl(self, data):
        LogD("unknown_decl :", data)

class NastolWallpapersRetriever:

    def __init__(self,CatalogName,StartPage,pageRangeEnd,outputDir):
        self.__CatalogName = CatalogName
        self.__StartPage = int(StartPage)
        self.__EndPage = int(pageRangeEnd)
        self.__outputDir = outputDir

        self.__ThreadsDownloads=[]
        self.__PrintStatusThread=None
        self.__CurrentSimultaneousDownloads=0
        self.__MaximumSimultaneousDownloads=100

        self.__sslContext = ssl._create_unverified_context()
        self.__RestSleepSeconds = 5
        self.__PagesWIthError=[]
        self.__CurrentPageProcessed=0
        self.__IsWorking=False
        self.__ErrorsDownloadingCount=0

    def StartRetrieving(self):
        self.__IsWorking = True
        self.__PrintStatusThread = threading.Thread(target=self.__StartStatusPrinting)
        self.__PrintStatusThread.start()
        if self.__StartPage >= 1 and self.__EndPage >= 1 :
            if self.__StartPage <= self.__EndPage:
                Range=range(self.__StartPage,self.__EndPage+1)
            else:
                Range=list(reversed(range(self.__EndPage,self.__StartPage)))
            for pageNum in Range:
                try:
                    #LogI("PROCESSING PAGE :",pageNum)
                    self.__CurrentPageProcessed = pageNum
                    WallpapersURLsList = self.__GetWallpapersInfoPagesList(pageNum)
                    if WallpapersURLsList != None and WallpapersURLsList.__len__() == 0 :
                        self.__PagesWIthError.append(pageNum)
                    elif WallpapersURLsList != None:
                        self.__StartRetrievingOriginResolutionWallpapers(WallpapersURLsList)
                    while self.__CurrentSimultaneousDownloads > self.__MaximumSimultaneousDownloads:
                        LogI("Maximum simultaneous downloads count occurred, sleep ",self.__RestSleepSeconds,"seconds")
                        time.sleep(self.__RestSleepSeconds)
                except UnicodeDecodeError:
                    LogE("Unicode decode error occurred for page",pageNum)

        for t in self.__ThreadsDownloads:
            t.join()
        self.__IsWorking=False
        self.__PrintStatusThread.join()
        del self.__ThreadsDownloads[:]
        self.__ThreadsDownloads=[]


    def __StartStatusPrinting(self):
        while(self.__IsWorking):
            self.__printStatus()
            time.sleep(0.2)

    def __printStatus(self):
        sys.stdout.write('\r')
        sys.stdout.write("Processing page num : "+str(self.__CurrentPageProcessed))
        sys.stdout.write(" Current Count of threads : "+str(self.__CurrentSimultaneousDownloads))
        sys.stdout.write(" Error download images count =  : "+str(self.__ErrorsDownloadingCount))

        
    
    def __GetWallpapersInfoPagesList(self,PageNum):
        InfoPageURL = NastolRootURL+"/"+self.__CatalogName+"/page/"+str(PageNum)+"/"

        LogD("Open URL : ",InfoPageURL)
        try:
            CatalogParser = NastolCatalogPageParser()
            CatalogParser.feed(str(urllib2.urlopen(InfoPageURL,context=self.__sslContext).read()))
            return CatalogParser.ListImageURL
        except urllib2.URLError:
            LogE("Error opening due to urllib2.URLError : "+InfoPageURL)
            self.__ErrorsDownloadingCount+=1
        except httplib.IncompleteRead:
            LogE("Error opening due to httplib.IncompleteRead : "+InfoPageURL)
            self.__ErrorsDownloadingCount+=1

    def __DownloadOriginResolutionWallpaperFromInfoPage(self,page):
        self.__CurrentSimultaneousDownloads+=1
        WallpaperName=page[-page[::-1].index("/"):][:-5]
        FinalFilePath=self.__outputDir+"\\"+WallpaperName+".jpg"
        #LogI("Start new thread, counts = ",self.__CurrentSimultaneousDownloads)
        if not os.path.isfile(FinalFilePath):
            try:
                WallpaperInfoPageParser = NastolWallpaperInfoPageParser()
                LogD("Open URL : ",page)
                WallpaperInfoPageParser.feed(str(urllib2.urlopen(page,context=self.__sslContext).read()))

                sourceURL = NastolRootURL+WallpaperInfoPageParser.sourceURL
                if sourceURL != "":
                    #LogI("Downloading ",sourceURL,"to",FinalFilePath)
                    urllib.urlretrieve(sourceURL, FinalFilePath)
                else:
                    LogE("Error downloading ",WallpaperName,"Source URL cannot be retrieved")
            except UnicodeDecodeError:
                LogE("Error Downloading Wallpaper UnicodeDecodeError ",WallpaperName)
                self.__ErrorsDownloadingCount+=1
            except httplib.IncompleteRead:
                LogE("Error Downloading Wallpaper IncompleteRead ",WallpaperName)
                self.__ErrorsDownloadingCount+=1
            except urllib.ContentTooShortError:
                LogE("Error Downloading Wallpaper ContentTooShortError ",WallpaperName)
                self.__ErrorsDownloadingCount+=1
        else:
            pass
            #LogI("SKIPPING already downloaded file :",FinalFilePath)
        self.__CurrentSimultaneousDownloads-=1
        #LogI("Thread finished count = ",self.__CurrentSimultaneousDownloads)

    def __StartRetrievingOriginResolutionWallpapers(self,WallpapersInfoPagesList):
        for page in WallpapersInfoPagesList:
             thread = threading.Thread(target=NastolWallpapersRetriever.__DownloadOriginResolutionWallpaperFromInfoPage, args=(self,page))
             self.__ThreadsDownloads.append(thread)
             thread.start()
