#!/usr/bin/python
#
# calibrate.py
#
# Calibration code modified from David Kittle's vecmath_v5.py
#
# Vector math + stage calculations
# Daniel Marks
# Written May 26, 2011
#

import sys
import os
import time
import math
import XPS_C8_drivers as xps

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.pyplot as plt
import numpy as np

import eCamera
import Image
import vecmath 

THRESHOLD=1
ROI_MIN=512
MAX_ITERS=10

############################################################
# calibration class
#
# Camera calibration class
#
# Written by: Steve Feller
# Date: 8/27/12

############################################################


class calibration()

  #establish StageControl
  sc=StageControl()                         #StageControl class

  #establish camera tiling
  rotaxis=Vec(0.0,1.0,1.0).unitvec()        # (0.0,1.0,1.0)
  rotang=0.0                                # rotation angle
  vertspan=10.0
  horizspan=vertspan*(3288.0/4384.0)
  ctr=Vec(0.0,-TRANSY,0.0)
  rad=100.0
  ct=CameraTiling(vertspan,horizspan,ctr,rad,rotaxis,rotang)
  ct.load_tiling('alternating.csv')

  #establish StageSolver
  st=StageSolver(rotaxis,rotang)
  st.setnq(Vec(-1.0,DEFQY,DEFQZ))
  st.setdisplacement(ctr)   
  st.initstage2()

  #establish camera interface
  mci = eCamera.eCamera(0,0)                #camera interface class
  
  #establish projector interface (and projected image)
  proj_img=Image();

  #define FPA parameters (sdf - move to config file)
  FPA={'width':'4384','height':'3288','iFOVx':'0.002365','iFOVy':'0.00227'}
 
  #define camera values (read from file)
  camDict={'1':{'az':'1','el':,'2','theta':'0'}}

  #define full ROI and ROI
  fullROI = [0,0,FPA['width'],FPA['height']]

  

  #get list of cameras
  cam_list = mci.getCamList

  ########################################
  # init
  ########################################
  def init(filename):
    return

  ########################################
  # calibrate_all
  ########################################
  def calibrate_all():
    current_cam_list = mci.get_Camlist()
    starti=current_cam_list.index(1)
    endi=current_cam_list.index(226) #len(current_cam_list)
    for index in range(starti,endi):
        if current_cam_list[index]>181:
            print 'Done'  # these cameras aren't reliably capable of being found
        else:
            find_nm2_justmeasure(current_cam_list[index],path,ROIsize)
    return

  ########################################
  # find_center
  #
  # cam - camera hole
  # cx  - pixel x position
  # cy  - pixel y position
  ########################################
  def find_pixel( cam, cx, cy ):
   
    Xest=cx                            #estimated X value
    Yest=cy                            #estimated Y value

    #generate ROI (assume less that ROI_MIN)
    roi=[cx-ROI_MIN/2,cy-ROI_MIN/2, ROI_MIN, ROI_MIN] 

    #loop MAX_ITERS until error acceptable
    for c in range(MAX_ITERS):

      #move to expected position in az/el coordinates
      #sdf-check with Dan, but I believe -1 => az/el coordinates
      az = camDict[cam]['az']+FPA[iFOVx]*Xest;
      el = camDict[cam]['el']+FPA[iFOVy]*Yest;
      st.enterposstage(-1, az, el)
   
      #calculate position
      Xest,Yest = get_position( cam, roi)

      #Calculate Error (distance from desired location)
      d=((cx-Xest)*(cx-Xest)+(cy-Yest)*(cy-Yest))**(0.5)

      if( d < THRESHOLD ):
        break;

      #estimate new Xest,Yest (need to account for rotation)
      Xest=cx-Xest;
      Yest=cy-Yest;
    
   return Xest, Yest, d   
    

  ########################################
  # get_position
  # 
  # function to extract center of projected image
  ########################################
  def get_position(cam, roi):
    #capture image
    im=capture_image(cam, roi, 1)

    #cross correlate
    x,y = correlate2(im, testim)

    return x,y

  ########################################
  # capture_image
  #
  # sdf - needs to be rewritten
  #
  # Inputs:
  #   roi - Region of interest to capture
  #   bin_value = level of binning, 1 for full pixels
  #   camera_hole = hole number
  ########################################
  def capture_image(camera_hole, roi,bin_value):
    
    #sdf refernce directive?       
    #t=time.time()

    # Set capture ROI:
    mci.nextCaptureROI(roi, bin_val)
    mci.snap_image(camera_hole)       

    # Set back to full ROI:
    mci.nextCaptureROI(fullROI, 1)

    #sdf refernce directive?       
    #print 'Cap time: ', time.time()-t
    return mci.nump

  ########################################
  # correlate
  #
  # replaced the original xcorr2 written by David Kittle
  #
  # Performs cross correlation of projected and measured images
  ########################################
  def correlate2
    # Find through iteration the nm for each camera
    img=Image.open("Ifilter.png")
    Ifilt=np.asarray(proj_img) 

    roi = [FPA['width']/2-ROIsize
    Iraw = capture_image(
    # Take image:


    Iraw=cap_image(ROIsize,1,camera_hole)  # Change for image size
    vcenter=[(np.size(Iraw,0)/2), (np.size(Iraw,1)/2)]
    #[C,Cc]=zone_pl.xcorr2w(Iraw,Ifilt)
    
    if (ROIsize > 512) or (ROIsize == 0):
        [C,Cc]=zone_pl2.xcorr2gpuv2(Iraw,Ifilt)  # GPU is faster for > 512
    else:
        [C,Cc]=zone_pl2.xcorr2w(Iraw,Ifilt)   
        
    [col,row]=zone_pl.max2(Cc)
    return col,row,vcenter

  ########################################
  # align
  #
  # Function to align the camera coordinates with the global coordinates
  # of the calibration system.
  ########################################
  def align():
    print "Need to write align code\n"
    return

  # Aditional functions to take data: -------------------------------------------------
  def take_data(icamno, iposx, iposy):
    st.enterposstage(icamno, iposx, iposy)
    [alpha, beta, dx, dz]=st.movestage()
    time.sleep(.3)

    return alpha, beta, dx, dz


  ########################################
  # function to find norms for 
  ########################################
  def find_norms(st,mci,camera_hole,path,ROIsize):
     [alpha, beta, dx, dz]=take_data(st,camera_hole, 0,0)
     [col,row,vcenter]=xcorr2(st,mci,camera_hole,ROIsize)
     # Save data:
     #path='/home/mosaic/Desktop/2012_05_21/7_05/nr_nmcorr/'
     filename=path+"nr_nm_just.txt" 
     if camera_hole==1:
        strs='Camera, alpha, beta, dx, dz, x error, y error, DEFQY='+str(DEFQY)+', DEFQZ='+str(DEFQZ)+'\n'
        fo=open(filename,"w":
)  #(s w is overwrite
        fo.write(strs)
     else: 
        fo=open(filename,"rw+")  # w is overwrite
        
     strs='nm, '+str(camera_hole)+ ','+ str(alpha)+ ','+ str(beta)+ ','+ str(dx)+ ','+ str(dz)+','+str(col-vcenter[1])+','+str(row-vcenter[0])+'\n'
     fo.seek(0,2)
     fo.write(strs)
          
     # Save image:
     #path='/home/mosaic/Desktop/2012_05_21/7_05/nr_nmcorr/'
     filename=path+'cam_'+str(camera_hole)+'.jpeg'
     II=zone_pl.cap_image(2048,1,camera_hole)
     imsave(II,filename)


  ############################(s############
  # find_pixel
  #
  # Find a projection that maps to the given pixel
  ########################################
  def find_pixel( camera, x, y)
    print "Need to write find_pixel code\n"
    return theta, phi
  
  ########################################
  # find_projection
  # 
  # Find the center in pixel coordinates of a given projection
  ########################################
  def find_projection( cam,theta,phi)
    print "Need to write find_pixel code\n"
    return x, y 

  def run()
    print "\n"
    return


########################################
# main
# 
# Command line interface function for testing
########################################
def main()
   c = calibration()
   c.calibrate_all()       
            
if __name__ == "__main__":        
  main()
      
        
    
    
    
 
