__author__ = 'vladimir'
import urllib2
import urllib
import ssl
import threading
import time
import os
from Utils import *
from HTMLParser import HTMLParser
GFRoot="https://www.goodfon.ru"

class GoodFonImagePageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.imageURI=""

    def handle_starttag(self, tag, attrs):
        #LogD("START_TAG :", tag)
        if tag == "a":
            #LogD("a tag entering:" , "AND ATTRS = ",attrs)
            try:
                if attrs[1][0] == "id" and attrs[1][1] == "im" and attrs[0][0] == "href" :
                    URI = attrs[0][1]
                    self.imageURI=URI
                    LogI("Image URI found : ",URI)
            except:
                pass

class GoodFonCatalogPageParser(HTMLParser):

    def __init__(self,rootElm):
        HTMLParser.__init__(self)
        self.ListImageURL=[]
        self.BoolInTab=False
        self.root=rootElm

    def handle_starttag(self, tag, attrs):
        #LogD("START_TAG :", tag)
        if tag == "div":
            #LogD("div tag entering:" , "AND ATTRS = ",attrs)
            try:
                if attrs[0][0] == "class" and attrs[0][1] == "tabl_td" :
                    self.BoolInTab = True
                    #LogD("tabl_td found")

            except:
                pass
        elif tag == "a":
            #LogD("a tag entering:" , "AND ATTRS = ",attrs)
            if self.BoolInTab == True and attrs[0][0] == "href":
                URL = attrs[0][1]
                LogI("Found Image URL : ", URL)
                self.ListImageURL.append(URL)
                self.BoolInTab = False

class GoodFonWallpaperInfoPageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.originResolutionValue = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            #LogD("a tag entering:" , "AND ATTRS = ",attrs)

            id = getAttrByKey("id",attrs)
            if id == "img" :
                URI = getAttrByKey("href",attrs)
                self.originResolutionValue = str(URI[-15:])[str(URI[-15:]).index("/")+1:-1]
                #LogD("Origin resolution found ",self.originResolutionValue)

def waitUntilAllowedToDownload():
    AllowedToDownload = False
    while not AllowedToDownload:
        try:
            LogI("Check if we can download images from GF...")
            context = ssl._create_unverified_context()
            urllib2.urlopen("https://img3.goodfon.ru/original/2800x1919/7/4f/fentezi-devushki-lotosy.jpg",context=context).read()
            AllowedToDownload = True
        except urllib2.HTTPError:
            LogE("HTTP ERROR wait another 5 minutes")
            time.sleep(300)

def findPicturesURLInCatalog(root,CatalogUrl):

    parser = GoodFonCatalogPageParser(root)
    context = ssl._create_unverified_context()
    print "Open URL : ",CatalogUrl
    try:
        parser.feed(str(urllib2.urlopen(CatalogUrl,context=context).read()))
        return parser.ListImageURL
    except urllib2.URLError:
        print "Error opening : "+CatalogUrl

def downloadImageFromGFURL(GFURL,imageName,resolution,outputFilePath):
    parser = GoodFonImagePageParser()
    context = ssl._create_unverified_context()
    URL = str(GFURL)+"/download/"+str(imageName)+"/"+str(resolution)+"/"
    LogI("Open URL : ",URL)
    try:
        parser.feed(str(urllib2.urlopen(URL,context=context).read()))

        imageURL = parser.imageURI

        LogI("Downloading image "+imageName+" to file ",outputFilePath)
        urllib.urlretrieve(imageURL,outputFilePath)
        if int(os.path.getsize(outputFilePath)) == 0:
            LogE("Error to download",imageName," waiting image to be available")
            os.remove(outputFilePath)
            waitUntilAllowedToDownload()
            urllib.urlretrieve(imageURL,outputFilePath)
    except urllib2.URLError:
        LogE("Error opening : "+URL)
    except IOError:
        LogE("IOError , Failed to download : "+imageURL)

def DownloadOriginalResolutionImage(GFURL,imageName,outputFilePath):
    parser = GoodFonWallpaperInfoPageParser()
    context = ssl._create_unverified_context()
    URL = str(GFURL)+"/wallpaper/"+str(imageName)+".html"
    LogI("Open URL : ",URL)
    try:
        parser.feed(str(urllib2.urlopen(URL,context=context).read()))

        OriginalResolution = parser.originResolutionValue
        downloadImageFromGFURL(GFURL,imageName,OriginalResolution,outputFilePath)
    except urllib2.URLError:
        LogE("Error opening : "+URL)

def DownloadAllImagesFromGoodFonPage(PageURI,outputDir):
    waitUntilAllowedToDownload()
    URIs = findPicturesURLInCatalog(GFRoot,GFRoot+"/"+PageURI)
    threads=[]
    if URIs != None:
        for URI in URIs:

            name = URI[11:-5]
            #print "NAME = " + name
            FinalFilePath=outputDir+"\\"+name+".jpg"
            if not os.path.isfile(FinalFilePath):
                thread = threading.Thread(target=DownloadOriginalResolutionImage, args=(GFRoot, name,FinalFilePath))
                threads.append(thread)
                thread.start()
            else:
                LogI("File",FinalFilePath,"already exists, Skipping it")
    for t in threads:
        t.join()