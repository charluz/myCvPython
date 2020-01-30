# -*- encoding: utf-8 -*-
"""
Gamma Tuning Tool
"""
import sys
import numpy as np
import math
import cv2, time

import tkinter as TK
import threading
# import socket
import argparse
import scipy.interpolate as spi

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.pylab as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

#---- Use site-packages modules


from cyTkGUI.cy_ViPanel import tkViPanel
from cyTkGUI.cy_ViPanel import tkV3Frame, tkH3Frame,  tkH2Frame, tkV2Frame
from cyTkGUI.cy_tkButtons import XsvButtonStack, tkButton
from cyTkGUI.cy_tkMatplot import tkMatplotFigure

from cy_Utils.cy_TimeStamp import TimeStamp

from mainGUI import MainGUI
from curve_ubox import curvePoints, CurveSplineFit

###########################################################
# Argument Parser
###########################################################
# parser = argparse.ArgumentParser()
# parser.add_argument("-m", '--host', type=str, default='192.168.137.87',
# 	help='The host machine: localhost or IP of remote machine, \
# 			or local:xxxx.jpg to use local test image file.')
# parser.add_argument("-p", '--port', type=int, default=8080,
# 	help='The port on which to connect the host')
# parser.add_argument("-j", '--jpg', type=str, default='test001.jpg',
# 	help='The jpeg file to display')
# # parser.add_argument('--jpeg_quality', type=int, help='The JPEG quality for compressing the reply', default=70)
# args = parser.parse_args()


#---------------------------------------------------------
# Main thread functions
#---------------------------------------------------------
def onClose():
	global tkRoot
	tkRoot.quit()
	tkRoot.destroy()
	pass


def _draw_cross_line(fig, point, x_range, y_range):
	"""
	@param	fig										the figure to draw cross lines
	@param	point								the control point in (x, y) tuple
	@param	x_range, y_range		python range object.
	"""
	vline_x = [point[0] for i in y_range]
	vline_y = [i for i in y_range]

	hline_x = [i for i in x_range]
	hline_y = [point[1] for i in x_range]

	fig.plot(point[0], point[1], 'o',  color='red')
	fig.plot(vline_x, vline_y, color='red', linewidth=2, linestyle='dotted')
	fig.plot(hline_x, hline_y, color='red', linewidth=2, linestyle='dotted')
	pass


def initialize_active_point():
	global ctrl_buttons, CtrlPoints, mainGUI, curve_fig

	#-- get current control point
	index = ctrl_buttons.get_active_index()
	point = CtrlPoints.get_point(index)

	#-- set x-bar, y-bar accordingly
	mainGUI.xBar.set(point[0])
	mainGUI.yBar.set(point[1])

	#-- draw cross line at current control point
	x_range = range(CtrlPoints.x_min, CtrlPoints.x_max)
	y_range = range(CtrlPoints.y_min, CtrlPoints.y_max)
	_draw_cross_line(curve_fig, point,  x_range, y_range)
	pass

def update_active_point(ctrlButtons, CtrlPoints):
	# print(ctrlButtons.buttonObject.get_value())
	# print(ctrlButtons.get_active_index())
	active_index = ctrlButtons.get_active_index()


#---------------------------------------------------------
# Main thread Entry
#---------------------------------------------------------

#----------------------------------------------------
# MainGUI Initialization
#----------------------------------------------------
print("[INFO] Starting main GUI...")
tkRoot = TK.Tk()
mainGUI = MainGUI(tkRoot)

tkRoot.wm_protocol("WM_DELETE_WINDOW", onClose)

#-- Load control points configuration
if sys.argv[1]:
	f_gma_points = sys.argv[1]
	CtrlPoints = curvePoints(pt_file=f_gma_points, debug=True)
	print("[INFO] Found and loaded gamma sample points ...")

#-- format the text list of the points
if CtrlPoints:
	ctrl_points = CtrlPoints.points


ctrl_buttons = mainGUI.ctrlButtons
texts = []
X = []
Y = []
for i, p in enumerate(ctrl_points):
	texts.append("P{:<2d}: X={:<3d}, Y={:<3d}".format(i, p[0], p[1]))
	X.append(p[0])
	Y.append(p[1])
ctrl_buttons.set_button_text(texts, idx=-1)

#-- fit curve
print("[INFO] Fitting curve ...")
curve_fit = CurveSplineFit(X, Y, deg=3)
curve_x, curve_y = curve_fit.get_curve()

print("[INFO] Plotting curve ...")
curve_fig = mainGUI.curveFig
if False:
	print("--- X: ",X)
	print("--- Y: ",Y)
	print("--- x: ",curve_x)
	print("--- y: ",curve_y)
curve_fig.plot(X, Y, 'o', curve_x, curve_y)

#----------------------------------------------------------------------
# Draw cross line on current active point
#----------------------------------------------------------------------
initialize_active_point()


print("[INFO] Updating figure ...")
curve_plt = mainGUI.curveForm
curve_plt.update_figure()

#----------------------------------------------------
# Main Loop
#----------------------------------------------------
tkRoot.mainloop()
