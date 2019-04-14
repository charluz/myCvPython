#!/usr/bin/python

import os, sys
import cv2
import argparse
import numpy as np

gRawImgFile = "undefined.raw"

gRawWidth = 1920
gRawHeiht = 1080
gRawBits = 12
gRawBayerType = 'B'

gOutputDir = None
gBatchMode = False


gImgRepoRoot = repr(os.getcwd())
gImgRepoCurr = gImgRepoRoot
gRawBaseName = ""

gIsShowBayerImage = 0
gIsShowRawGray = 1
gIsShowRawRGB = 0

gIsSaveBayerColor = 1
gIsSaveRawGray = 1
gIsSaveRawRGB = 1

gMaxImgShowWidth = 640

bayerCode_Table = {
    'bayerR':  0,
    'bayerGr': 1,
    'bayerGb': 2,
    'bayerB':  3
}

bayer2gray_code = {
    0: cv2.COLOR_BAYER_RG2GRAY,
    1: cv2.COLOR_BAYER_GR2GRAY,
    2: cv2.COLOR_BAYER_GB2GRAY,
    3: cv2.COLOR_BAYER_BG2GRAY
}

bayer2bgr_code = {
    0: cv2.COLOR_BAYER_RG2BGR,
    1: cv2.COLOR_BAYER_GR2BGR,
    2: cv2.COLOR_BAYER_GB2BGR,
    3: cv2.COLOR_BAYER_BG2BGR
}

bayerImg_geometric = { # (X, Y)
    0: (300, 140),  # R
    1: (340, 170),  # Gr
    2: (380, 200),  # Gb
    3: (420, 230),  # B
    100: (300, 300), # RawGray
    101: (330, 330) # RawRGB
}


###########################################################
# Bayer Color lookup functions
###########################################################
def bayerCode_Name2ID(szName):
    return bayerCode_Table.get(szName, 0)


###########################################################
# Message Box with OK button
###########################################################
def messageBoxOK(title, msg):
    box = Toplevel()
    box.title(title)
    Label(box, text=msg).pack()
    Button(box, text='OK', command=box.destroy).pack()



###########################################################
# Functions : Create working folders
###########################################################
def createDirectory(name):
    if not os.path.exists(name):
        try:
            os.mkdir(name)
        except:
            messageBoxOK("Error", "Can't create folder : \n"+repr(name))
            return ""
        #print("Directory ", name, " created.")
    else:
        #print("Directory ", name, " already exists.")
        pass

    return name



def createImageRepoRoot(cwd, name):
    # print(cwd + name)
    return createDirectory(cwd+name)


###########################################################
# Function : Callback of Button RESET
###########################################################
def cbfnButtonReset():
    print("<<<cbfnButtonReset>>>")
    cv2.destroyAllWindows()
    # btnRaw.config(text='Open RAW', command=cbfnButtonOpenRaw, bg='LightGreen')
    # textvarStatusBar.set("")



###########################################################
# Functions : saveRawGrayImage
###########################################################

def saveRawGrayImage(rawImg, bayerCode, bits):
    if bits > 8:
        matRaw = rawImg << (16-bits)
    else:
        matRaw = rawImg

    ## Bayer2Gray
    code = bayer2gray_code.get(bayerCode, cv2.COLOR_BAYER_RG2GRAY)
    matGray = cv2.cvtColor(matRaw, code)

    #print("saveRawGrayImage: shape before >> 8: ", matGray.shape)
    if bits > 8:
        matGray = matGray >> 8  # / 256
    #print("saveRawGrayImage: shape after >> 8: ", matGray.shape)
    matGray = matGray.astype(np.uint8)
    #print("saveRawGrayImage: shape after astype(np.uint8) >> 8: ", matGray.shape)

    # print(matGray)
    win_title = "RAW_Gray"
    if gIsShowRawGray:
        #print("Display {} image ...".format(win_title))
        cv2.namedWindow(win_title, cv2.WINDOW_NORMAL)
        x, y = bayerImg_geometric.get(100)
        cv2.moveWindow(win_title, x, y)
        h, w = matGray.shape
        if w > gMaxImgShowWidth:
            h = int( (h * gMaxImgShowWidth) / w)
            w = gMaxImgShowWidth
        cv2.resizeWindow(win_title, w, h)
        cv2.imshow(win_title, matGray)

    jpgGray = gRawBaseName + "_" + win_title + '.jpg'

    #print("Save {} image ...".format(jpgGray))
    if gIsSaveRawGray: cv2.imwrite(jpgGray, matGray)

    ## Bayer2BGR
    code = bayer2bgr_code.get(bayerCode, cv2.COLOR_BAYER_RG2BGR)
    matBGR = cv2.cvtColor(matRaw, code)
    if bits > 8:
        matBGR = matBGR / 256
    matBGR = matBGR.astype(np.uint8)

    win_title = "RAW_RGB"
    if gIsShowRawRGB:
        #print("Display {} image ...".format(win_title))
        cv2.namedWindow(win_title, cv2.WINDOW_NORMAL)
        x, y = bayerImg_geometric.get(101)
        cv2.moveWindow(win_title, x, y)

        #print(matBGR.shape)
        h, w, _ = matBGR.shape
        if w > gMaxImgShowWidth:
            h = int( (h * gMaxImgShowWidth) / w)
            w = gMaxImgShowWidth
        cv2.resizeWindow(win_title, w, h)
        cv2.imshow(win_title, matBGR)

    jpgRGB = gRawBaseName + "_" + win_title + '.jpg'
    #print("Saving {} image ...".format(jpgRGB))
    if gIsSaveRawRGB: cv2.imwrite(jpgRGB, matBGR)

    return


###########################################################
# Functions : saveSplitedImage
###########################################################
def saveSplitedImage(imgGray, bayerCode, isShowImg, winName):

    if not gIsSaveBayerColor:
        return

    img = imgGray.astype(np.uint8)
    matImg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if bayerCode == 0:      # R
        matImg[:,:,0] = 0
        matImg[:,:,1] = 0
    elif bayerCode == 1 or bayerCode == 2:    # Gr / Gb
        matImg[:,:,0] = 0
        matImg[:,:,2] = 0
    else:                   # B
        matImg[:,:,1] = 0
        matImg[:,:,2] = 0

    if not winName:
        winName = 'bayerColor'+str(bayerCode)
    # print(gRawBaseName+winName)
    cv2.imwrite(gRawBaseName+"_"+winName+".jpg", matImg)

    if isShowImg:
        cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
        w = matImg.shape[1]
        h = matImg.shape[0]
        if w > gMaxImgShowWidth:
            h = int((h * gMaxImgShowWidth) / w)
            w = gMaxImgShowWidth
        cv2.resizeWindow(winName, w, h)
        x, y = bayerImg_geometric.get(bayerCode)
        cv2.moveWindow(winName, x, y)
        cv2.imshow(winName, matImg)

    return matImg

def save_raw_RGrGbB_image(img1, img2, img3, img4):
    global gbayerMean
    saveSplitedImage(img1, 0, gIsShowBayerImage, "RAW_R")
    saveSplitedImage(img2, 1, gIsShowBayerImage, "RAW_Gr")
    saveSplitedImage(img3, 2, gIsShowBayerImage, "RAW_Gb")
    saveSplitedImage(img4, 3, gIsShowBayerImage, "RAW_B")
    szRawMean="Raw_Mean (R/Gr/Gb/B): {:.1f}, {:.1f}, {:.1f}, {:.1f}".format(gbayerMean[0], gbayerMean[1], gbayerMean[2], gbayerMean[3])
    return szRawMean

def save_raw_GrRBGb_image(img1, img2, img3, img4):
    global gbayerMean
    saveSplitedImage(img1, 1, gIsShowBayerImage, "RAW_Gr")
    saveSplitedImage(img2, 0, gIsShowBayerImage, "RAW_R")
    saveSplitedImage(img3, 3, gIsShowBayerImage, "RAW_B")
    saveSplitedImage(img4, 2, gIsShowBayerImage, "RAW_Gb")
    szRawMean="Raw_Mean (R/Gr/Gb/B): {:.1f}, {:.1f}, {:.1f}, {:.1f}".format(gbayerMean[1], gbayerMean[0], gbayerMean[3], gbayerMean[2])
    return szRawMean

def save_raw_GbBRGr_image(img1, img2, img3, img4):
    global gbayerMean
    saveSplitedImage(img1, 2, gIsShowBayerImage, "RAW_Gb")
    saveSplitedImage(img2, 3, gIsShowBayerImage, "RAW_B")
    saveSplitedImage(img3, 0, gIsShowBayerImage, "RAW_R")
    saveSplitedImage(img4, 1, gIsShowBayerImage, "RAW_Gr")
    szRawMean="Raw_Mean (R/Gr/Gb/B): {:.1f}, {:.1f}, {:.1f}, {:.1f}".format(gbayerMean[2], gbayerMean[3], gbayerMean[0], gbayerMean[1])
    return szRawMean

def save_raw_BGbGrR_image(img1, img2, img3, img4):
    global gbayerMean
    saveSplitedImage(img1, 3, gIsShowBayerImage, "RAW_B")
    saveSplitedImage(img2, 2, gIsShowBayerImage, "RAW_Gb")
    saveSplitedImage(img3, 1, gIsShowBayerImage, "RAW_Gr")
    saveSplitedImage(img4, 0, gIsShowBayerImage, "RAW_R")
    szRawMean="Raw_Mean (R/Gr/Gb/B): {:.1f}, {:.1f}, {:.1f}, {:.1f}".format(gbayerMean[3], gbayerMean[2], gbayerMean[1], gbayerMean[0])
    return szRawMean


def save_raw_XXXX_image(img1, img2, img3, img4):
    messageBoxOK('ERROR', 'Unknown bayer type !!')


###########################################################
# Function : Split Bayer Components
###########################################################
def splitBayerRawU16(bayerdata, width, height, rawBits, bayerType):
    '''
    @Brief
        To split R/Gr/Gb/B components from Bayer Raw image input.
    @In
        bayerdata   : Raw image input (from io.open/io.read)
        width, height   : size of Raw image
        rawBits     : number of bits per pixel
    @Out
        boolean : indicating success/failure
    @Globals
        bayerImgC1, bayerImgC2, bayerImgC3, bayerImgC4 : sub-images of R/Gr/Gb/B.
            Size of sub-image is (widht/2, height/2).
    '''
    global bayerImgC1, bayerImgC2, bayerImgC3, bayerImgC4

    imgW, imgH = (int(width>>1))<<1, (int(height>>1)<<1)
    simgW, simgH =int(imgW>>1), int(imgH>>1)
    bayerImgC1, bayerImgC2, bayerImgC3, bayerImgC4 = [np.zeros([simgH, simgW, 1], np.uint8) for x in range(4)]

    if not gBatchMode: print("splitBayerRawU16: width %d -> %d, height %d -> %d" % (imgW, simgW, imgH, simgH))

    bitshift = rawBits-8

    #print("--- Reshaping raw image --- {} to {}x{}".format(bayerdata.shape[0], imgW, imgH))
    try:
        imgRaw = bayerdata.reshape(imgH, imgW)
    except:
        print("ERROR: Reshaping raw image failed!")
        cbfnButtonReset()

    #print("--- Saving RawGRAY image ---")
    saveRawGrayImage(imgRaw, bayerType, rawBits)

    #print("--- Calculate RAW means ---")
    global gbayerMean
    gbayerMean = np.zeros(4, dtype=np.float)
    if rawBits > 8:
        bayerImg = imgRaw[0:imgH+1:2, 0:imgW+1:2]
        gbayerMean[0] = bayerImg.mean()
        bayerImgC1 = bayerImg >> bitshift

        bayerImg = imgRaw[0:imgH+1:2, 1:imgW+1:2]
        gbayerMean[1] = bayerImg.mean()
        bayerImgC2 = bayerImg >> bitshift

        bayerImg = imgRaw[1:imgH+1:2, 0:imgW+1:2]
        gbayerMean[2] = bayerImg.mean()
        bayerImgC3 = bayerImg >> bitshift

        bayerImg = imgRaw[1:imgH+1:2, 1:imgW+1:2]
        gbayerMean[3] = bayerImg.mean()
        bayerImgC4 = bayerImg >> bitshift

    else:
        bayerImgC1 = imgRaw[0:imgH+1:2, 0:imgW+1:2]
        gbayerMean[0] = bayerImgC1.mean()
        #print("Bayer mean: {:.2f}".format(gbayerMean[0]))
        #print(bayImgC1[476:497, 612:633])

        bayerImgC2 = imgRaw[0:imgH+1:2, 1:imgW+1:2]
        gbayerMean[1] = bayerImgC2.mean()
        #print("Bayer mean: {:.2f}".format(gbayerMean[1]))
        #print(bayImgC2[476:497, 612:633])

        bayerImgC3 = imgRaw[1:imgH+1:2, 0:imgW+1:2]
        gbayerMean[2] = bayerImgC3.mean()
        #print("Bayer mean: {:.2f}".format(gbayerMean[2]))
        #print(bayImgC3[476:497, 612:633])

        bayerImgC4 = imgRaw[1:imgH+1:2, 1:imgW+1:2]
        gbayerMean[3] = bayerImgC4.mean()
        #print("Bayer mean: {:.2f}".format(gbayerMean[3]))

    # print("Bayer mean: C1: {:.1f} C2: {:.1f} C3: {:.1f} C4: {:.1f} ".format(gbayerMean[0], gbayerMean[1], gbayerMean[2], gbayerMean[3]))

    save_bayer_img = {
        0:save_raw_RGrGbB_image,
        1:save_raw_GrRBGb_image,
        2:save_raw_GbBRGr_image,
        3:save_raw_BGbGrR_image
    }

    func = save_bayer_img.get(bayerType, save_raw_XXXX_image)
    szMean = func(bayerImgC1, bayerImgC2, bayerImgC3, bayerImgC4)
    print("==== ", szMean)    #-- show Bayer mean values

    return True


###########################################################
# Button Function : LoadRAW
###########################################################
def cbfnButtonLoadRaw(rawImg):
    try:
        #print("--- A ---")
         splitBayerRawU16(rawImg, gRawWidth, gRawHeight, gRawBits, gRawBayerType)
        #print("--- B ---")
    except:
        cbfnButtonReset()
        return

###########################################################
# Button Function : OpenRAW
###########################################################
def cbfnButtonOpenRaw(rawFileName):
    global gimgRaw, gRawImgFile, gRawBaseName


    bits = gRawBits
    try:
        if bits > 8:
            gimgRaw = np.fromfile(rawFileName, dtype=np.uint16)
        else:
            gimgRaw = np.fromfile(rawFileName, dtype=np.uint8)
    except:
        print('ERROR: Failed to open file : ', rawFileName)
        cbfnButtonReset()
        return

    #-------------------------------------------------------
    # Create root repository folder for output images
    #-------------------------------------------------------
    if gOutputDir == None:
        gImgRepoRoot = os.path.dirname(gRawImgFile)
        os.chdir(gImgRepoRoot)
        gImgRepoRoot = createImageRepoRoot(gImgRepoRoot, "/_imageRepo")
        # print(gImgRepoRoot)

        # Create folder to save output images for loaded RAW image
        baseName = os.path.basename(gRawImgFile)

        base, _ = os.path.splitext(baseName)
        gImgRepoCurr = gImgRepoRoot + "/" + base
        #print("Target image repo ", gImgRepoCurr)
        if createDirectory(gImgRepoCurr):
            os.chdir(gImgRepoCurr)

        gRawBaseName = base
        #print(gRawBaseName)

    else :
        gImgRepoCurr = gOutputDir
        if createDirectory(gImgRepoCurr):
            os.chdir(gImgRepoCurr)
        # Create folder to save output images for loaded RAW image
        baseName = os.path.basename(gRawImgFile)
        gRawBaseName, _ = os.path.splitext(baseName)


    # to Load and Parse RAW images
    cbfnButtonLoadRaw(gimgRaw)

    return



###########################################################
# Button Function : Exit Main Window
###########################################################
def cbfnButtonMainExit():
    print("<<<cbfnButtonMainExit>>>")
    cv2.destroyAllWindows()
    return



###########################################################
# Print Program arguments
###########################################################
def print_arguments():
    global gCallByGui
    print("--- Program Arguments -----------------------------------------------")
    print("Called by GUI: ", gCallByGui)
    argstr = "rawImage"
    print(argstr, ": ", gRawImgFile)
    argstr = "width"
    print(argstr, ": ", gRawFormat[argstr])
    argstr = "height"
    print(argstr, ": ", gRawFormat[argstr])
    argstr = "bayer"
    print(argstr, ": ", gRawFormat[argstr])
    argstr = "bits"
    print(argstr, ": ", gRawFormat[argstr])
    argstr = "output"
    print(argstr, ": ", gOutputDir)
    print("---------------------------------------------------------------------")
    print()



###########################################################
# RAW Format JSON Parser
###########################################################
def conf_json_load(strJson):
    import json
    global gRawFormat, gProgConf

    #jsonDict = {}
    conf_json = strJson
    try:
        with open(conf_json, "r") as f:
            jsonDict = json.load(f)
    except:
        print("Error: failed to load configuration file ... ", conf_json)
        jsonDict = None

    #print(jsonDict)
    if jsonDict:
        gRawFormat["width"] = jsonDict["width"]
        gRawFormat["height"] = jsonDict["height"]
        gRawFormat["bits"] = jsonDict["bits"]
        gRawFormat["bayer"] = jsonDict["bayer"]

        gProgConf["showBayerColor"] = jsonDict["showBayerColor"]
        gProgConf["showRawGray"] = jsonDict["showRawGray"]
        gProgConf["showRawRGB"] = jsonDict["showRawRGB"]

        gProgConf["saveBayerColor"] = jsonDict["saveBayerColor"]
        gProgConf["saveRawGray"] = jsonDict["saveRawGray"]
        gProgConf["saveRawRGB"] = jsonDict["saveRawRGB"]

    return jsonDict




###########################################################
# MainEntry
###########################################################

gRawFormat = {
    "width"         : 1600,
    "height"        : 1200,
    "bits"          : 10,
    "bayer"         : 3,    #-- "bayer cdoe: R=0, Gr=1, Gb=2, B=3"
}


gProgConf = {
    "showBayerColor"    : False,
    "showRawGray"       : False,
    "showRawRGB"        : True,

    "saveRawRGB"        : True,
    "saveRawGray"       : True,
    "saveBayerColor"      : True,
}


if __name__ == "__main__":
    #-------------------------------------
    # Parse arguements
    #-------------------------------------
    argparse.ArgumentParser()
    parser = argparse.ArgumentParser()
    parser.add_argument('rawImg', help="input RAW image file name")
    parser.add_argument('--gui', nargs='?', const=1, type=int, default=0, help='Called by a GUI wrapper if specified')
    parser.add_argument('--conf', help='JSON file for default RAW format.')
    parser.add_argument("--width", type=int, help='the width of the RAW image')
    parser.add_argument("--height", type=int, help='the height of the RAW image')
    parser.add_argument("--bayer", choices=['R', 'Gr', 'Gb', 'B'], help='bayer type of starting pixel\navailable options:R, Gr, Gb, B.')
    parser.add_argument("--bits", type=int, help='number of bits per pixel')
    parser.add_argument("--output", type=str, help='the directory name to store output files')
    parser.add_argument("--batch", nargs='?', const=1, type=int, default=0, help='running in batch mode if specified')
    parser.add_argument("--ROI", help='+x+y*w+h to specify ROI of RAW image.')
    args = parser.parse_args()

    # print(args.conf)
    if args.conf:
        conf_json_load(args.conf)

    if args.width and args.height:
        gRawFormat["width"]     = args.width
        gRawFormat["height"]    = args.height

    if args.bits:
        gRawFormat["bits"]      = args.bits

    if args.bayer:
        gRawFormat["bayer"]     = args.bayer

    if args.output:
        gOutputDir = args.output


    #-------------------------------------
    # Initialize globals
    #-------------------------------------
    gRawImgFile = args.rawImg
    gCallByGui = args.gui
    if args.batch:
        gBatchMode = True
    else:
        gBatchMode = False

    gRawWidth, gRawHeight = gRawFormat["width"], gRawFormat["height"]
    gRawBits = gRawFormat["bits"]
    gRawBayerType = gRawFormat["bayer"]

    gIsShowBayerImage = gProgConf["showBayerColor"]
    gIsShowRawGray = gProgConf["showRawGray"]
    gIsShowRawRGB = gProgConf["showRawRGB"]

    gIsSaveBayerColor = gProgConf["saveBayerColor"]
    gIsSaveRawGray = gProgConf["saveRawGray"]
    gIsSaveRawRGB = gProgConf["saveRawRGB"]

    # print("Show options: {} {} {}".format(gIsShowRawGray, gIsShowRawRGB, gIsShowBayerImage))
    # print("Save options: {} {} {}".format(gIsSaveRawGray, gIsSaveRawRGB, gIsSaveBayerColor))

    if False:   #-- Debug only !!
        print_arguments()

    cbfnButtonOpenRaw(gRawImgFile)

    if not gCallByGui and not gBatchMode:
        while True:
            if 27 == cv2.waitKey(100):
                cv2.destroyAllWindows()
                break