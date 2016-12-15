import sys
import urllib2
import urllib
import ssl
import threading
import time
import os
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

    def __init__(self,rootElm):
        HTMLParser.__init__(self)
        self.root=rootElm
        self.ListImageURL=[]

    def handle_starttag(self, tag, attrs):
        #LogD("START_TAG :", tag," attrs = ",attrs)
        if tag == "a":
            #LogD("a tag entering:" , "AND ATTRS = ",attrs)
            cl = getAttrByKey("class",attrs)
            if cl == "screen-link":
                href = getAttrByKey("href",attrs)
                if href != None:
                    LogD("Found Image URL : ", href)
                    self.ListImageURL.append(href)

def ParseWallpapperInfoPage(infoPageURL,Wallpaper_pages_URLs_dict):
    WallpaperInfoPageParser = NastolWallpaperInfoPageParser()
    context = ssl._create_unverified_context()
    # LogI("wallpaperName - ",WallpaperName)
    LogI("Open URL : ",infoPageURL)
    WallpaperInfoPageParser.feed(str(urllib2.urlopen(infoPageURL,context=context).read()))
    if WallpaperInfoPageParser.sourceURL != "":
        WallpaperName=infoPageURL[-infoPageURL[::-1].index("/"):][:-5]
        Wallpaper_pages_URLs_dict[WallpaperName] = WallpaperInfoPageParser.sourceURL

def findNastolSourceURLsInCatalog(root,CatalogUrl,dictToAppend):

    context = ssl._create_unverified_context()
    LogI("Open URL : ",CatalogUrl)
    try:
        CatalogParser = NastolCatalogPageParser(root)
        CatalogParser.feed(str(urllib2.urlopen(CatalogUrl,context=context).read()))
        Wallpaper_pages_info_list = CatalogParser.ListImageURL

        Wallpaper_pages_URLs_dict={}

        threads=[]
        for url in Wallpaper_pages_info_list:
            thread = threading.Thread(target=ParseWallpapperInfoPage, args=(url, Wallpaper_pages_URLs_dict))
            threads.append(thread)
            thread.start()
            #ParseWallpapperInfoPage(url,Wallpaper_pages_URLs_dict)
        for t in threads:
            t.join()


        dictToAppend.update(Wallpaper_pages_URLs_dict)
    except urllib2.URLError:
        LogE("Error opening : "+CatalogUrl)

def DownloadAllImagesFromNastolPage(PageURI,pageRangeStart,pageRangeEnd,outputDir):
    try:
        NameURLDict={}
        if pageRangeStart == pageRangeEnd:
            findNastolSourceURLsInCatalog(NastolRootURL,NastolRootURL+"/"+PageURI+"/page/"+str(pageRangeStart)+"/",NameURLDict)
        elif pageRangeStart >= 1 and pageRangeEnd >= 1 :
            if pageRangeStart < pageRangeEnd:
                forRange=range(pageRangeStart,pageRangeEnd)
            else:
                forRange=list(reversed(range(pageRangeEnd,pageRangeStart)))

            for pageNum in forRange:
                try:
                    findNastolSourceURLsInCatalog(NastolRootURL,NastolRootURL+"/"+PageURI+"/page/"+str(pageNum)+"/",NameURLDict)
                except UnicodeDecodeError:
                    print "Unicode decode error occurred"
        LogD("URI's found : ",NameURLDict)
        threads=[]
        LogD("URI's found : ",NameURLDict)
        if NameURLDict != None:
            for name in NameURLDict.keys():
                # print "NAME = " + name
                FinalFilePath=outputDir+"\\"+name+".jpg"
                OriginalURLImage = NastolRootURL+NameURLDict[name]
                if not os.path.isfile(FinalFilePath):
                    LogI("Downloading ",OriginalURLImage," to ", FinalFilePath)
                    thread = threading.Thread(target=urllib.urlretrieve, args=(OriginalURLImage, FinalFilePath))
                    threads.append(thread)
                    thread.start()
                else:
                    LogI("File",FinalFilePath,"already exists, Skipping it")
        for t in threads:
            t.join()
    except UnicodeDecodeError:
        print "Unicode decode error occurred"