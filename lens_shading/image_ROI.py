#!/usr/bin/python

import os, sys
# from tkinter import *  # Tk, Label, Entry, Radiobutton, IntVar, Button
# from tkinter import filedialog
import cv2
import numpy as np

# import matplotlib.pyplot as plt
# from matplotlib import cm
# from mpl_toolkits.mplot3d import Axes3D

MAX_AB = lambda A, B : A if A > B else B
MIN_AB = lambda A, B : A if A < B else B

def interpolateXY(P0, P1, fraction):
    ''' To interpolate coordinate of a point which is on the line from  P0 to P1 
        fraction is counted from P0
    '''

    ''' 
    XX=abs(x0-x1), YY=abs(y0-y1), X= int(fraction * XX), Y= int(fraction * YY)
    '''
    X = int(fraction * abs(P0[0]-P1[0]))
    Y = int(fraction * abs(P0[1]-P1[1]))
    
    if P0[0] >= P1[0]:
        x = MAX_AB(P1[0], P0[0] - X)
    else:
        x = MIN_AB(P1[0], P0[0] + X)

    if P0[1] >= P1[1]:
        y = MAX_AB(P1[1], P0[1] - Y)
    else:
        y = MIN_AB(P1[1], P0[1] + Y)

    return (x, y)


class drawROI():
    _property = {
        'enabled'       : True,
        'lwidth'        : 1,
        'lcolor'        : (0, 255, 0),
    }

    gWinName=''
    gMatImg=np.array([])
    X = Y = W = H = 0
    def __init__(self, winName, matImg, **kwargs):
        self.gWinName = winName
        self.gMatImg = matImg
        #cv2.imshow(self.gWinName, self.gMatImg)
        for argKey, argVal in kwargs.items():
            #print("ImageROI: argKey= ", argKey, " argVal= ", argVal)
            if argKey == 'X':
                '''coordinate X of top-left vertex '''
                self.X = argVal
            elif argKey == 'Y':
                '''center coordinate Y'''
                self.Y = argVal
            elif argKey == 'W':
                '''size W'''
                self.W = argVal
            elif argKey == 'H':
                '''size H'''
                self.H = argVal
            else:
                pass
                
    def set_center(self, x, y):
        ''' Set coordinate (x, y) of the ROI center'''
        self.X = x
        self.Y = y
        
    def set_size(self, w, h):
        ''' Set size (w, h) of the ROI'''
        self.W = w
        self.H = h

    def set_property(self, **kwargs):
        ''' Set properities :
                enabled:    True/False -- show or no show
                lwidth:     width of rectangle line
                lcolor:     the color to draw rectangle (R, G, B)
        '''
        for argkey, argval in kwargs.items():
            if argkey == 'enabled':
                self._property['enabled'] = argval   # True or False
            elif argkey == 'lwidth':
                self._property['lwidth'] = argval   # line width
            elif argkey == 'lcolor':
                self._property['lcolor'] = argval   # line color
            else:
                pass

    def get_property(self, protKey):
        '''To query property with following key:
                'enabled', 'lwidth', 'lcolor'
        '''
        return self._property[prot]
    
    def show(self):
        ''' To draw the ROI rectangle onto the image'''
        if self._property['enabled'] == True:
            halfW = int(self.W/2)
            halfH = int(self.H/2)
            p1 = (self.X-halfW, self.Y-halfH)
            p2 = (self.X+halfW, self.Y+halfH)
            color = self._property['lcolor']
            lwidth = self._property['lwidth']
            cv2.rectangle(self.gMatImg, p1, p2, color, lwidth)
            cv2.imshow(self.gWinName, self.gMatImg)


###########################################################
# MainEntry 
###########################################################


def main():
    winName='imageROI'
    winPosX, winPosY = 150, 100
    #matImg = cv2.imread('Building.jpeg', cv2.IMREAD_UNCHANGED)
    matImg = cv2.imread('church.jpg', cv2.IMREAD_UNCHANGED)
    # print(matImg.shape)
    cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
    cv2.moveWindow(winName, winPosX, winPosY)
    #cv2.imshow(winName, matImg)

    imgH = matImg.shape[0]
    imgW = matImg.shape[1]
    imgCenterX = int(imgW / 2)
    imgCenterY = int(imgH / 2)
    print('image WxH = ', imgW, ' x ', imgH)

    roiW = int(imgW/10)
    roiH = int(imgH/10)
    #--------------------------
    # -- Center ROI
    #--------------------------
    #roiC=drawROI(winName, matImg.copy(), X=10, Y=20, W=100, H=50)
    mat2draw = matImg.copy()
    roiC=drawROI(winName, mat2draw)
    roiC.set_center(imgCenterX, imgCenterY)
    roiC.set_size(roiW, roiH)
    roiC.show()

    #--------------------------
    # -- Diagonal: Qudrant Q1, Q2, Q3, Q4
    #--------------------------

    fraction = 0.95
    # -- Q1
    Po = (imgCenterX, imgCenterY)
    Pv = (imgW, 0)
    x, y = interpolateXY(Po, Pv, fraction)
    print("Q1: P0= ", Po, " P1= ", Pv, " P= ", (x, y))
    roiQ1 = drawROI(winName, mat2draw, X=x, Y=y, W=roiW, H=roiH)
    roiQ1.show()

    # -- Q2
    Po = (imgCenterX, imgCenterY)
    Pv = (0, 0)
    x, y = interpolateXY(Po, Pv, fraction)
    print("Q2: P0= ", Po, " P1= ", Pv, " P= ", (x, y))
    roiQ2 = drawROI(winName, mat2draw, X=x, Y=y, W=roiW, H=roiH)
    roiQ2.show()

    # -- Q3
    Po = (imgCenterX, imgCenterY)
    Pv = (0, imgH)
    x, y = interpolateXY(Po, Pv, fraction)
    print("Q3: P0= ", Po, " P1= ", Pv, " P= ", (x, y))
    roiQ3 = drawROI(winName, mat2draw, X=x, Y=y, W=roiW, H=roiH)
    roiQ3.show()

    # -- Q4
    Po = (imgCenterX, imgCenterY)
    Pv = (imgW, imgH)
    x, y = interpolateXY(Po, Pv, fraction)
    print("Q4: P0= ", Po, " P1= ", Pv, " P= ", (x, y))
    roiQ4 = drawROI(winName, mat2draw, X=x, Y=y, W=roiW, H=roiH)
    roiQ4.show()

    ''' Just for Debug
    cv2.namedWindow('Original')
    cv2.imshow('Original', matImg)
    '''
    cv2.waitKey(0)



if __name__ == "__main__":
    main()