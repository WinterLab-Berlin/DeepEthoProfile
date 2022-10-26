#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 11:03:08 2022

@author: Andrei Istudor
"""

import av
import pandas as pd
import numpy as np
import cv2
# from skimage.transform import resize

from Logger import Logger


verbose = False

class DataReaderAV():
    def __init__(self, logger, videoFilePath, annFilePath=None): 
        self.videoFile = videoFilePath
        self.annFile = annFilePath
        self.logger = logger
        
        self.avContainer = None
        self.videoStream = None
    
        self.annData = None

        self.seekIndex = None
        self.seekOffset = 0
        self.totalFrames = 1
    
    
    def open(self, streamId = 0, offset = 0):
        self.logger.log('open video {}, and ann {}'.format(self.videoFile, self.annFile), verbose)
        try:
            self.avContainer = av.open(self.videoFile)
            self.avContainer.streams.video[0].thread_type = "FRAME"

            self.videoStream = self.avContainer.streams.video[streamId]
            self.totalFrames = 5000 
            if(self.avContainer.streams.video[streamId].duration):
                self.totalFrames = (self.avContainer.streams.video[streamId].duration +1 )/ 40
            
            if (self.annFile is not None):
                self.annData = pd.read_csv(self.annFile, sep=';', header=1)

            if(offset > 0):
                i = 0
                for packet in self.avContainer.demux(self.videoStream):
                    if packet.size == 0:
                        self.logger.log('skip frames - demux empty packet', verbose)
                        break
                    i += 1
                    if(i >= offset):
                        break
                        
                
            return True
        except:
            self.logger.log('error opening video file: ' + self.videoFile, verbose)
            return False
        
        
        
    def readFrames(self, n):
        result = []
        index = 0
        
        if(self.videoStream != None and index < n):
            # self.logger.log('read {} frames'.format(n), verbose)
            finished = False
            
            for packet in self.avContainer.demux(self.videoStream):
                if packet.size == 0:
                    self.logger.log('demux empty packet', verbose)
                    break
                for frame in packet.decode():
                    crtVFrame = frame.to_ndarray(format='gray')
                    
                    h, w = crtVFrame.shape
                    if (h != 256 or w != 256):
                        #crop, pad and resize
                        # outFrame = np.zeros((w, w)) #, dtype=int)
                        # outFrame[177:527, :] = crtVFrame[90:440, :]
                        # crtVFrame = resize(outFrame, (256, 256)) #, cv2.INTER_AREA)
                        
                        crtVFrame = crtVFrame[90:440, :]
                        crtVFrame = cv2.copyMakeBorder(crtVFrame, 177, 177, 0, 0, cv2.BORDER_CONSTANT, None, 0)
                        crtVFrame = cv2.resize(crtVFrame, (256, 256)) 

                    # print(crtVFrame.size)
                    # print(crtVFrame.shape)
                    # print(crtVFrame[0].size)

                    
                    # self.logger.log('frame: {}, ts: {}'.format(frame.index, frame.pts), verbose)

                    crtRes = [frame.index, frame.pts, crtVFrame]
                    
                    #add annotation
                    if(self.annData is not None):
                        crtRes.append(self.annData.loc[frame.index, 'annotation'])
                        
                    result.append(crtRes)
                    index += 1
                    
                    if index >= n:
                        finished = True
                        break
                if finished:
                    break
                
        return result

    #TODO: 
    def buildSeekIndex(self):
        self.logger.log('build seek index - not implemented', verbose)
    
    def seek(self, n):
        if(self.seekIndex == None):
            self.buildSeekIndex()
        
        self.logger.log('seek frame {} - not implemented'.format(n), verbose)
        
if __name__ == '__main__':
    
    
    fullVideo = '/home/andrei/Videos/_originalRecordings/01_20180418_1200.mkv'
    fullAnnFile = '/home/andrei/Videos/_originalRecordings/ann_train/01_20180418_1200_RS.csv'
    
    shortVideo = '/home/andrei/Videos/_originalRecordings/x.mkv'
    vsv = '/home/andrei/Videos/tmp/pyAV/xs.mkv'
    videoFile = '/home/andrei/Videos/test/short_04_20180815_1200.mkv'
    
    logFile = '/home/andrei/Documents/GitHub/EthoProfiler/tmp/readerAV.log'
    log = Logger(logFile)
    
    dr = DataReaderAV(shortVideo, annFilePath=fullAnnFile, logger=log)
    if(dr.open()):
        print('test read')
        x = dr.readFrames(1)
        # print(x)
        # x = dr.readFrames(13)
        # print(x)
        
    
    
    
    
