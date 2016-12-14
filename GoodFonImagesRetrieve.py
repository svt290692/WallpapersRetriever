import urllib2
import urllib
import ssl
import sys
import threading
import time
import os
from HTMLParser import HTMLParser

GFRoot="https://www.goodfon.ru"
MResolution="1366x768"

def ConvertArgsToString(args):
    builder = ""
    for elm in args:
        builder=builder+str(elm)
    return builder

def LogI(*args):
    print "INFO : "+ConvertArgsToString(args)

def LogE(*args):
    print "ERROR : "+ConvertArgsToString(args)

def LogD(*args):
    print "DEBUG : "+ConvertArgsToString(args)

def getAttrByKey(key,attrs):
    attr = [item for item in attrs if item[0] == key]
    if attr.__len__() > 0 and attr[0].__len__() > 0:
        return attr[0][1]

    return None

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

Catalog =""
EndPage=1
StartPage=1
outputDir=""

if sys.argv.__len__() >= 2:
    Catalog = sys.argv[1]

    if sys.argv.__len__() >= 3:
        outputDir = sys.argv[2]

    if sys.argv.__len__() >= 4:
        EndPage = sys.argv[3]

    if sys.argv.__len__() >= 5:
        StartPage = sys.argv[4]


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