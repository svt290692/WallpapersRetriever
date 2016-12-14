import sys
from GoodFonAPI import DownloadAllImagesFromGoodFonPage
import urllib2
import urllib
import ssl
import threading
import time
import os
from Utils import *
from HTMLParser import HTMLParser
SourceType_GoofFon="GF"

SourceSite=""
Catalog =""
EndPage=1
StartPage=1
outputDir=""


#GF
# def parseSysArgs():
#     global Catalog
#     global EndPage
#     global StartPage
#     global outputDir
#     global SourceSite
#
#     if sys.argv.__len__() >= 2:
#         SourceSite = sys.argv[1]
#
#     if sys.argv.__len__() >= 3:
#         Catalog = sys.argv[2]
#
#     if sys.argv.__len__() >= 4:
#         outputDir = sys.argv[3]
#
#     if sys.argv.__len__() >= 5:
#         EndPage = sys.argv[4]
#
#     if sys.argv.__len__() >= 6:
#         StartPage = sys.argv[5]
#
# def startGoodFonRetrieving():
#     print "START RETRIEVING IMAGES"
#     if EndPage == StartPage:
#         DownloadAllImagesFromGoodFonPage(Catalog+"/index-"+str(EndPage)+".html",outputDir)
#     elif int(EndPage) > 1:
#         for i in range(int(StartPage),int(EndPage)):
#             try:
#                 print "RETRIEVING PAGE num ",i
#                 DownloadAllImagesFromGoodFonPage(Catalog+"/index-"+str(i)+".html",outputDir)
#             except UnicodeDecodeError:
#                 print "Unicode decode error occurred, cannot download page number ",i
#     elif int(EndPage) == -1:
#         while True:
#             DownloadAllImagesFromGoodFonPage(Catalog,outputDir)
#     else:
#         DownloadAllImagesFromGoodFonPage(Catalog,outputDir)
#
#
# parseSysArgs()
#
# if SourceSite == SourceType_GoofFon:
#     startGoodFonRetrieving()
#GF

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
        #LogD("START_TAG :", tag)
        if tag == "a":
            LogD("a tag entering:" , "AND ATTRS = ",attrs)
            cl = getAttrByKey("class",attrs)
            if cl == "screen-link":
                href = getAttrByKey("href",attrs)
                if href != None:
                    LogD("Found Image URL : ", href)
                    self.ListImageURL.append(href)

def findNastolSourceURLsInCatalog(root,CatalogUrl):

    CatalogParser = NastolCatalogPageParser(root)
    context = ssl._create_unverified_context()
    LogI("Open URL : ",CatalogUrl)
    try:
        CatalogParser.feed(str(urllib2.urlopen(CatalogUrl,context=context).read()))
        Wallpaper_pages_info_list = CatalogParser.ListImageURL
        Wallpaper_pages_URLs_list=[]

        for url in Wallpaper_pages_info_list:
            WallpaperInfoPageParser = NastolWallpaperInfoPageParser()

            # LogI("wallpaperName - ",WallpaperName)
            LogI("Open URL : ",url)
            WallpaperInfoPageParser.feed(str(urllib2.urlopen(url,context=context).read()))
            if WallpaperInfoPageParser.sourceURL != "":
                WallpaperName=url[-url[::-1].index("/"):][:-5]
                Wallpaper_pages_URLs_list.append(WallpaperInfoPageParser.sourceURL)

        return Wallpaper_pages_URLs_list
    except urllib2.URLError:
        LogE("Error opening : "+CatalogUrl)

def DownloadAllImagesFromNastolPage(PageURI,pageNum,outputDir):
    # waitUntilAllowedToDownload()
    URIs = findNastolSourceURLsInCatalog(NastolRootURL,NastolRootURL+PageURI+"/page/"+str(pageNum)+"/")
    threads=[]
    LogD("URI's fiuld : ",URIs)
    if URIs != None:
        for URI in URIs:
            pass
            # name = URI[11:-5]
            #print "NAME = " + name
            # FinalFilePath=outputDir+"\\"+name+".jpg"
            # if not os.path.isfile(FinalFilePath):
            #     thread = threading.Thread(target=DownloadOriginalResolutionImage, args=(GFRoot, name,FinalFilePath))
            #     threads.append(thread)
            #     thread.start()
            # else:
            #     LogI("File",FinalFilePath,"already exists, Skipping it")
    for t in threads:
        t.join()

DownloadAllImagesFromNastolPage("/fantasy",1,"D:")
# LogI("Image URI found : ","hello")

# print os.path.isfile("D:\\images\\col-price-open-your-mind.jpg")
# os.remove("D:\\images\\col-price-open-your-mind.jpg")
# # try:
#     context = ssl._create_unverified_context()
#     print urllib2.urlopen("https://img3.goodfon.ru/original/2800x1919/7/4f/fentezi-devushki-lotosy.jpg",context=context).read()
# except urllib2.HTTPError:
#     print "HTTP ERROR"
#                     time.sleep(int(RestTime))
# parser = GoodFonWallpaperInfoPageParser()
# context = ssl._create_unverified_context()
# try:
#     parser.feed(str(urllib2.urlopen("https://www.goodfon.ru/wallpaper/monster-tight-storm-lightning.html",context=context).read()))
# except urllib2.URLError:
#     print "Error opening "

# requiredDownloadPages = 2
#
# for i in range(1,requiredDownloadPages+1):
#     path = "catalog/nature/index-"+str(i)+".html"
#     # path = "catalog/fantasy/random"


# print 'Argument List:', str(sys.argv)



# try:
#     context = ssl._create_unverified_context()
#     if str(urllib2.urlopen("https://img2.goodfon.ru/original/1366x768/5/27/art-mingsong-jia-devushka.jpg",context=context).read()).__len__() > 0:
#         DownloadAllImagesFromGoodFonPage("catalog/fantasy/random")
# except:
#     print "error"
#     pass

#downloadImageFromGFURL("https://www.goodfon.ru","noch-nebo-oblaka-zvezdy-luna","1366x768","D:\\images\\outfile.jpg")
#print str(urllib2.urlopen("https://www.goodfon.ru",context=context).read())

# arr= [("hello",2),("hello",4),("fuu",5),("foo",7)]
#
# print str([item for item in arr if item[0] == "foo"][0][1]) # 7

# for ch in "HELLO"[::-1]:
#     print ch
# print str("HELLLO"[-3:-1])