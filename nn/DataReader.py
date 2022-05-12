#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:10:03 2020

@author: andrei
"""

#read video
import cv2
import pandas as pd
import numpy as np

#import torch
#import torch.nn
#from torch import optim

import matplotlib.pyplot as plt

from collections import deque
from numpy import mean

#def image2Tensor(src):
    # out = src.copy()
    # out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
    # out = out.transpose((2, 1, 0)).astype(np.float64) / 255
    # return torch.tensor(out)

class DataReader():
    def __init__(self, videoFilePath, annFilePath = None): #trackingFilePath, 
        self.videoFile = videoFilePath
        self.annFile = annFilePath
        # self.trackingFile = trackingFilePath

        self.annData = None
            
        self.trackDataIndex = 1
        self.crtFrameIndex = 1
        
        self.xDeq = deque('', 10)
        self.yDeq = deque('', 10)
        
        self.totalFrames = 0
        
    # def loadData(self):
        #self.cageData = pd.read_csv(self.annFile, sep=';', header=0, nrows=1)
        #print(self.cageData)
        
        # self.annData = pd.read_csv(self.annFile, sep=';', header=0, skiprows=2)
        # self.trackDataIndex = 1
        #print(self.annData)
        
    def openVideo(self):
        self.cap = cv2.VideoCapture(self.videoFile)

        if (self.cap.isOpened() == False): 
            print("Error opening video stream or file")
            return False
        
        self.totalFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if (self.annFile is not None):
            self.annData = pd.read_csv(self.annFile, sep=';', header=1)


        else:
            print('empty ann file name, video: ', self.videoFile)
            # return False

        return True #self.openPosData()

    def reset(self):
        self.cap = 0
        if(self.openVideo()):
            self.trackDataIndex = 1
            self.crtFrameIndex = 1
        else:
            print("reset failed")
            
    def readFrame(self):
        if(self.cap.isOpened()):

            ret, frame = self.cap.read()
            
            if ret == True:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # frame = cv2.resize(frame, (256, 256), interpolation = cv2.INTER_AREA)
                self.crtFrameIndex = self.crtFrameIndex + 1
                return frame #/ 255 # - 1
            else:
                # print("failed to read frame")
                return None
            
    def skipFrame(self):
        if(self.cap.isOpened()):
        
            if(self.cap.grab()):
                self.crtFrameIndex = self.crtFrameIndex + 1
                return True
            else:
                return False
        
                
    def readFrames(self, noFrames):
        frameSet = []
        iFrames = 1;
        
        for i in range(noFrames):
            newFrame = self.readFrame()
            if newFrame is not None:
                frameSet.append(newFrame)
            else:
                frameSet = None
                break
            
        return frameSet
    
    def setIndex(self, index):
        if(index < self.crtFrameIndex):
            print("seeking forward not supported (yet)")
            return False
        
        # print('set index')
        while(index > self.crtFrameIndex):
            if(self.skipFrame() is False):
                print('grab frame failed, reached the end of the video')
                return False
        # print('index set')
        
        return True
    
    
    def readProcData(self, index, noFrames):
        if(self.setIndex(index) == False):
            print("read training data failed at index: ", index )
            return -1, -1
        frames = self.readFrames(noFrames)
        if frames is not None:
            return frames
        else:
            return -1
        
    
    def getProcessingData(self, index, noFrames, splitSize=0.5):
        #TODO: check whether there are enough frames
        frameSet = self.readProcData(index, noFrames) #, posFeatures
        
        if frameSet is -1:
            return -1#, 0

        y = np.array(frameSet)
        x = y.reshape(noFrames, 1, 256, 256)

        return x#, posFeatures
    
    def getTrainingData(self, index, noFrames):
        #TODO: check whether there are enough frames
        frameSet = self.getProcessingData(index, noFrames) 
        
        if frameSet is -1:
            return -1, 0#, 0
        else:
            annData = self.annData.loc[index : index+noFrames-1, 'annotation']
            annDataNP = np.array(annData, dtype=np.long)        
            
            return frameSet, annDataNP 


#%matplotlib inline
if __name__ == '__main__': 
    videoFile = '20180420_0000_eat_sleep.mkv_ROI.avi'
    annotationFile = '20180420_0000_eat_sleep.mkv_out.csv'
    plt.figure(figsize=(10,10))
    
    
    reader = dataReader(videoFile, annotationFile, annotationFile)
    reader.openVideo()
    reader.setIndex(9400)
    # f = reader.readFrame()
    noFrames = 10
    frameSet = []
    
    # reader.loadData()
    yt, posFeatures = reader.readData(noFrames)
    
    for i in range(noFrames):
        crtFrame = reader.readFrame()
        #crtFrame2 = crtFrame / 255
        #frameSet.append(crtFrame2)
        
    frameSet = reader.readFrames(noFrames)
    y = np.array(frameSet)
    x = y.reshape(noFrames, 1, 150, 150)
    xt = torch.from_numpy(x)
    
    
    plt.subplot(221), plt.imshow((crtFrame + 1) * 255, cmap='gray')
    crtFrame2 = crtFrame + 1
    plt.subplot(222), plt.imshow(crtFrame2 , cmap='gray')
        
    restData = reader.annData.loc[reader.trackDataIndex:reader.trackDataIndex + noFrames-1, 'mouse.x':'mouse.h']
    
    #nf=10
    #x = reader.readFrames(nf)
    #x = np.array(x)
    #x = x.reshape(nf, 1, 150, 150)
    
    #plt.subplot(221), plt.imshow(f, cmap='gray')
    #plt.subplot(222), plt.imshow(x[1], cmap='gray')
    
    
    #reader.loadData()
