import sys
from GoodFonAPI import DownloadAllImagesFromGoodFonPage
from NastolAPI import NastolWallpapersRetriever
import urllib2
import urllib
import ssl
import threading
import time
import os
from Utils import *
from HTMLParser import HTMLParser
SourceType_GoofFon="GF"
SourceType_Nastol="Nastol"

SourceSite=""
Catalog =""
EndPage=1
StartPage=1
outputDir=""


def parseSysArgs():
    global Catalog
    global EndPage
    global StartPage
    global outputDir
    global SourceSite

    if sys.argv.__len__() >= 2:
        SourceSite = sys.argv[1]

    if sys.argv.__len__() >= 3:
        Catalog = sys.argv[2]

    if sys.argv.__len__() >= 4:
        outputDir = sys.argv[3]

    if sys.argv.__len__() >= 5:
        EndPage = sys.argv[4]

    if sys.argv.__len__() >= 6:
        StartPage = sys.argv[5]

def startGoodFonRetrieving():
    print "START RETRIEVING IMAGES"
    if EndPage == StartPage:
        DownloadAllImagesFromGoodFonPage(Catalog+"/index-"+str(EndPage)+".html",outputDir)
    elif int(EndPage) > 1:
        for i in range(int(StartPage),int(EndPage)):
            try:
                print "RETRIEVING PAGE num ",i
                DownloadAllImagesFromGoodFonPage(Catalog+"/index-"+str(i)+".html",outputDir)
            except UnicodeDecodeError:
                print "Unicode decode error occurred, cannot download page number ",i
    elif int(EndPage) == -1:
        while True:
            DownloadAllImagesFromGoodFonPage(Catalog,outputDir)
    else:
        DownloadAllImagesFromGoodFonPage(Catalog,outputDir)

parseSysArgs()

if SourceSite == SourceType_GoofFon:
    startGoodFonRetrieving()
elif SourceSite == SourceType_Nastol:
    retriever = NastolWallpapersRetriever(Catalog,StartPage,EndPage,outputDir)
    retriever.StartRetrieving()
    # DownloadAllImagesFromNastolPage(Catalog,int(StartPage),int(EndPage),outputDir)







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