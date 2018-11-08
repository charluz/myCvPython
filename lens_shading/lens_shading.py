#!/usr/bin/python

from tkinter import *  # Tk, Label, Entry, Radiobutton, IntVar, Button
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt

'''
from tkFileDialog import askopenfilename

That code would have worked fine in Python 2.x, but it is no longer valid. 
In Python 3.x, tkFileDialog was renamed to filedialog.
'''

###########################################################
# Message Box with OK button
###########################################################
def messageBoxOK(title, msg):
    box = Toplevel()
    box.title(title)
    Label(box, text=msg).pack()
    Button(box, text='OK', command=box.destroy).pack()



###########################################################
# Function : Split Bayer Components
###########################################################
def splitBayerRawWord(bayerdata, width, height, rawBits):
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
        simg1, simg2, simg3, simg4 : sub-images of R/Gr/Gb/B. 
            Size of sub-image is (widht/2, height/2).
    '''
    global simg1, simg2, simg3, simg4

    imgW, imgH = (int(width>>1))<<1, (int(height>>1)<<1)
    simgW, simgH =int(imgW>>1), int(imgH>>1)
    simg1, simg2, simg3, simg4 = [np.zeros([simgH, simgW, 3], np.uint8) for x in range(4)]

    print("width %d -> %d, height %d -> %d" % (imgW, simgW, imgH, simgH))

    box = Toplevel()
    #box.title(title)
    lbl = Label(box, text='Process RAW ...')
    lbl.pack()


    for rr in range (0, imgH, 2):       # process two rows at a time, R/Gr, Gb/B
        row_even_offset = rr * imgW * 2     # 2 bytes per pixels
        row_odd_offset = row_even_offset + (imgW * 2)
        for cc in range (0, imgW, 2):
            col_offset = cc * 2
            ## color_1 (bayer top-left)
            lbyte = bayerdata[row_even_offset+col_offset]
            hbyte = bayerdata[row_even_offset+col_offset+1]
            pix_v = (hbyte*256 + lbyte) >> (rawBits-8)
            simg1[rr>>1,cc>>1] = [pix_v for x in range(3)]

            ## color_2 (bayer top-right)
            lbyte = bayerdata[row_even_offset+col_offset+2]
            hbyte = bayerdata[row_even_offset+col_offset+3]
            pix_v = (hbyte*256 + lbyte)  >> (rawBits-8)
            simg2[rr>>1,cc>>1] = [pix_v for x in range(3)]

            ## color_3 (bayer bottom-left)
            lbyte = bayerdata[row_odd_offset+col_offset]
            hbyte = bayerdata[row_odd_offset+col_offset+1]
            pix_v = (hbyte*256 + lbyte)  >> (rawBits-8)
            simg3[rr>>1,cc>>1] = [pix_v for x in range(3)]

            ## color_4 (bayer bottom-right)
            lbyte = bayerdata[row_odd_offset+col_offset+2]
            hbyte = bayerdata[row_odd_offset+col_offset+3]
            pix_v = (hbyte*256 + lbyte)  >> (rawBits-8)
            simg4[rr>>1,cc>>1] = [pix_v for x in range(3)]

    # dismiss message box
    box.destroy()

    #print(simg4)
    plt.imshow(simg4)
    plt.show()
    plt.imsave('./simg4.jpg', simg4)

    return True


###########################################################
# Button Function : LoadRAW
###########################################################
def cbfnButtonLoadRaw():
    global btnRaw, rawdata
    print("Button: Load RAW")
    splitBayerRawWord(rawdata, int(txtlblRawWidth.get()), 
                    int(txtlblRawHeight.get()), 
                    int(txtlblRawBits.get()) )

###########################################################
# Button Function : OpenRAW
###########################################################
def cbfnButtonOpenRaw():
    global txtlblRawFName, btnRaw, rawdata
    txtlblRawFName.set(value=filedialog.askopenfilename() )
    rawfname = txtlblRawFName.get()
    #print(rawfname)
    try:
        f = open(rawfname, 'rb')
        rawdata = f.read()
        btnRaw.config(text='Load RAW', command=cbfnButtonLoadRaw)
    except:
        messageBoxOK('FileIO', 'Failed to open file :\n' + rawfname)
    '''
    with open(rawfname, 'rb') as in_file:
        rawdata = in_file.read()
        btnRaw.config(text='Load RAW', command=cbfnButtonLoadRaw)
    '''

###########################################################
# MainEntry 
###########################################################

winMain = Tk()
winMain.title('Lens Shading Viewer')
#winMain.geometry('300x150')

btnRaw = Button(winMain, text='Open RAW', command=cbfnButtonOpenRaw)
btnRaw.grid(row=0, column=0, pady=2)
txtlblRawFName = StringVar()
##txtlblRawFName.set(value='test')
lblRawFName = Label(winMain, width=48, textvariable=txtlblRawFName)
lblRawFName.grid(row=0, column=1, columnspan=8)


lblRawWidth = Label(winMain, text='Width')
lblRawWidth.grid(row=1, column=0, pady=2)
txtlblRawWidth = StringVar(value='2304')
entryRawWidth = Entry(winMain, bd=2, justify=LEFT, width=10, textvariable=txtlblRawWidth)
entryRawWidth.grid(row=1, column=1, sticky=W)

lblRawHeight = Label(winMain, text='Height')
lblRawHeight.grid(row=2, column=0, pady=2)
txtlblRawHeight = StringVar(value='1296')
entryRawHeight = Entry(winMain, bd=2, justify=LEFT, width=10, textvariable=txtlblRawHeight)
entryRawHeight.grid(row=2, column=1, sticky=W)


# def ShowChoice():
#     global bayerSelect
#     print(bayerSelect.get())

lblRawBayer = Label(winMain, text='Bayer')
lblRawBayer.grid(row=1, column=3, pady=2)
bayerSelect = IntVar(value=3)
bayer_config = [ ('R', 0, 2, 3), ('Gr', 1, 2, 4), ('Gb', 2, 3, 3), ('B', 3, 3, 4) ]
#bayer_config = [ ('R', 0), ('Gr', 1), ('Gb', 2), ('B', 3) ]
for bayer, val, row, col in bayer_config:
    btn = Radiobutton(winMain, text=bayer,
                  padx = 20, 
                  variable=bayerSelect, 
                  #command=ShowChoice,
                  value=val)
    btn.grid(row=row, column=col)
    btn.config(anchor=W, justify=LEFT, width=2)
    #print("Bayer= %s, Row= %d, Column= %d" % (bayer, row, col) )

lblRawBits = Label(winMain, text='Pixel Bits')
lblRawBits.grid(row=3, column=0, padx=2, pady=2)
txtlblRawBits = StringVar(value='10')
entryRawBits = Entry(winMain, bd=2, justify=LEFT, width=10, textvariable=txtlblRawBits)
entryRawBits.grid(row=3, column=1, sticky=W)

varBytePack = IntVar(value=0)
chkBytePack = Checkbutton(winMain, text='Packed', variable=varBytePack)
chkBytePack.grid(row=4, column=1, sticky=W)



winMain.mainloop()

