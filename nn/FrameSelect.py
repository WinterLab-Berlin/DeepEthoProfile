#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 14:51:16 2024

@author: Andrei Istudor andrei.istudor@gmail.com
"""

import numpy as np
from sympy.codegen.ast import float16

from EthoCNN import EthoCNN#, getTensors
import torch
from sklearn.metrics import accuracy_score
from random import randint, random
from os import path
import pandas as pd
# from pathlib import Path
import glob

import logging
logging.getLogger("libav").setLevel(logging.FATAL)
# import av
# av.logging.set_level(av.logging.PANIC)



# from DataReader import DataReader
from DataReaderAV import DataReaderAV
# from StackFrames import getTensors, getTestTensors
from Logger import Logger


logger: Logger
videoFile: str
annFile: str
finished: bool
stackSize: int
reader: DataReaderAV



bf =    [0, 0.6, 0.4, 0, 0.63, 0.63, 0.62, 0]
leave_078_out = [0, 0.73, 0.45, 0, 0.65, 0.65, 0.7, 0]
leave_06_out =    [0, 0.655, 0.55, 0.1, 0.72, 0.71, 0.72, 0]
leave_05_out =    [0, 0.65, 0.55, 0.1, 0.7, 0.68, 0.72, 0]
leave_04_out =    [0, 0.65, 0.55, 0.15, 0.74, 0.73, 0.72, 0.06]
leave_023_out =    [0, 0.66, 0.47, 0.05, 0.62, 0.61, 0.72, 0.06]
leave_01_out =    [0, 0.66, 0.49, 0.15, 0.6, 0.6, 0.7, 0.1]

# rev only [0, 0.61, 0.55, 0.3, 0.61, 0.67, 0.7, 0.23]
#split_5 [0, 0.75, 0.65, 0.41, 0.725, 0.705, 0.78, 0.38]
#split_6 [0, 0.74, 0.65, 0.36, 0.71, 0.7, 0.772, 0.36]

class FrameSelect():
    def __init__(self, logger, videoFile, annFile, offset, stackSize = 11):
        self.logger = logger
        self.videoFile = videoFile
        self.annFile = annFile
        self.reader = None
        self.stackSize = stackSize
        self.finished = True
        
    def startReader(self, offset=0):
        self.reader = DataReaderAV(self.logger, self.videoFile, self.annFile) 
        if(self.reader.open(offset=offset) is False):
            print(f'FS - cannot open video: {self.videoFile} with offset = {offset}')
            return False
        
        # print('reader initialized')
        self.finished = False
        return True
    
    def stopReader(self):
        if(self.reader is not None):
            self.reader.close()
        del self.reader
        
    def transCount(self, ann):
        crtAnn = ann[0]
        noTrans = 0
        for x in ann:
            if(x != crtAnn):
                crtAnn = x
                noTrans += 1
        return noTrans
    	
    def selectAnn(self, ann, checkSkip=True):
        # print('select stack')
        sAnn = -1
        skip = False

        annL = ann

        xx = self.transCount(ann)
        if(xx > 2):
            # print('too many transitions: ', xx, ', ann set is: ', ann)
            skip = True
            return 0, skip
        
        ii = int(len(ann)/2)
        i2 = int(ii/2)
        
        #remove unclassified frames
        if(annL.count(8) > 2):
            skip = True
            return 0, skip
        
        # print(ii)
        # print(i2)
        av = ann[ii]
        
        if(annL.count(av) < ii):
            am = max(annL, key=annL.count)
            
            if(av != am and annL.count(am) > annL.count(av) + 2):
                aaf = annL[i2:ii+i2+2]
                
                amc = aaf.count(am)
                axc = aaf.count(av)
                
                # if(av==0 or am == 0):
                #     print('change train ann from {} to {} in array: {}, extended: {}, i2={}, ii={}'.format(av, am, ann, aaf, i2, ii))
                if (amc > axc+1):
                    # print('change train ann from {} to {} in array: {}, extended: {}, i2={}, ii={}'.format(av, am, ann, aaf, i2, ii))
                    av = am
        sAnn = av
        
        if(checkSkip):
            mult = 1
            c = annL.count(av)
            if(c <= ii):
                # print('small, av = ', av, ', ann: ', ann)
                # mult += 0.1
                pass
            elif(c > ii + i2):
                # print('big')
                mult += 0.2
            else:
                mult += 0.1
                # print('--moderat, av = ', av, ', ann: ', ann)
                pass
            
            if(av == 0):        #drink
                if(random() < bf[0] * mult):
                    skip = True
                pass
            elif(av == 1):      #eat
                if(random() < bf[1]): # * mult):  #81
                    skip = True
            elif(av == 2):      #groom
                if(random() < bf[2]): # * mult):  #65
                    skip = True
            elif(av == 3):      #hang
                if(random() < bf[3]): # * mult):
                    skip = True
            elif(av == 4):      #mm
                if(random() < bf[4]): # * mult): #75
                    skip = True
            elif(av == 5):      #rear
                if(random() < bf[5]): # * mult):
                    skip = True
                pass
            elif(av == 6):      #rest
                if(random() < bf[6] * mult): #8
                    skip = True
            elif(av == 7):      #walk
                if(random() < bf[7]): # * mult):
                    skip = True

        return sAnn, skip
    
    def getTestSet(self, setSize, extra=False):
        outi = np.array(np.zeros((setSize, self.stackSize, 256, 256), dtype=np.float16))
        outa = np.array(np.zeros((setSize, self.stackSize), dtype=int))
        indexList = []
        ptsList = []
        i = 0

        for dataSegment in self.reader.readFrames(self.stackSize):
            if(len(dataSegment) < self.stackSize):
                # print('not enough frames left')
                break
            else:

                crtIm, crtAnn, crtIndex, crtPts = self.getTestImage(dataSegment, extra=True)
                # print('add image')
                
                # newIm = LUT[crtIm].astype(np.float16)
                crtIm = crtIm.astype(np.float16) / 256
                # crtIm -= 1
                
                outi[i] = crtIm
                outa[i] = crtAnn
                i += 1
                indexList.append(crtIndex)
                ptsList.append(crtPts)
                    
                if(i >= setSize):
                    # print('set complete')
                    break
        # print(outa.shape)
        # print(outi.shape)
        if(extra):
            return outi, outa, i, indexList, ptsList
        else:
            return outi, outa, i
        

    def getTestImage(self, data, extra = False):
        data = np.array(data, dtype=object)

        x = data[:, 2]
        y = data[:, 3]

        im = np.stack(x[::])
        # print(y.shape)

        if(extra):
            index = data[:, 0]
            pts = data[:, 1]
            return im.astype(np.float16), y.astype(np.uint8), index, pts
        else:
            return im.astype(np.float16), y.astype(np.uint8)

    
    def getTrainTuple(self):
        imS = np.zeros((self.stackSize, 256, 256), dtype=np.float16)
        ann = -1
        modify = True
        
        for dataSegment in self.reader.readFrames(self.stackSize):
            if(len(dataSegment) < self.stackSize):
                # print('not enough frames left')
                self.finished = True
                break
            else:
                if(modify and random() > 0.9):
                    modify = False
                crtIm, crtAnn, skip = self.getTrainImage(dataSegment, modify)
                if(skip):
                    continue
                
                if(crtAnn < 0):
                    print('should not get here! annotation = ', crtAnn)
                    self.finished = True
                    break
                else:
                    # print('add image')
                    # newIm = LUT[crtIm].astype(np.float16)
                    crtIm = crtIm.astype(np.float16) / 256
                    # newIm -= 1
                    
                    imS = crtIm
                    ann = crtAnn
                    break
                    
        return imS, ann, self.finished                    
                

    def getTrainImage(self, data, modify, train=False):
        # print('get stacked image')
        sIm = np.zeros((self.stackSize, 256, 256), dtype=np.float16)
        crtAnn = -1
        
        data = np.array(data, dtype=object)
        # print(data.shape)
        y = data[:, 3].tolist()
        x = data[:, 2]
                
        crtAnn, skip = self.selectAnn(y)
        if(skip):
            return sIm, crtAnn, skip
        else:
            if(modify):
                crtidx = 0
                sx = randint(0, 20) #30) #10
                sy = randint(0, 80) #90) #55
                flip = False
                tx = True
                ty = True
                if(random() > 0.8):
                    flip = True
                if(random() > 0.5):
                    tx = False
                if(random() > 0.5):
                    ty = False
                    
                for im in x:
                    # print('change im')
                    
                    if flip:
                        im = np.flip(im, 1)
                        
                    if tx:
                        if ty:
                            sIm[crtidx][:256-sy, sx:] = im[sy:, :256-sx]
                        else:
                            sIm[crtidx][sy:, sx:] = im[:256-sy, :256-sx]
                    else:
                        if ty:
                            sIm[crtidx][:256-sy, :256-sx] = im[sy:, sx:]
                        else:
                            sIm[crtidx][sy:, :256-sx] = im[:256-sy, sx:]
                    crtidx += 1
            else:
                sIm = np.stack(x[::])
            
        return sIm, crtAnn, skip
        


