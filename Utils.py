

DebugEnabled=False
def ConvertArgsToString(args):
    builder = ""
    for elm in args:
        builder=builder+str(elm)+" "
    return builder

def LogI(*args):
    print "INFO : "+ConvertArgsToString(args)

def LogE(*args):
    print "ERROR : "+ConvertArgsToString(args)

def LogD(*args):
    if DebugEnabled:
        print "DEBUG : "+ConvertArgsToString(args)

def getAttrByKey(key,attrs):
    attr = [item for item in attrs if item[0] == key]
    if attr.__len__() > 0 and attr[0].__len__() > 0:
        return attr[0][1]

    return None
