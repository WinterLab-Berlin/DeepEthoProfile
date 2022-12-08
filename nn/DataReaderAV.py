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

def mapAnn(oldAnn):
    newAnn = 2
    
    if(oldAnn == 1):                    # old drink
        newAnn = 0                      # new drink
    elif(oldAnn == 2):                  # old eat
        newAnn = 1                      # new eat
    elif(oldAnn == 4):                  # old groom 
        newAnn = 2                      # new mm
    elif(oldAnn == 5):                  # old hang
        newAnn = 3                      # new hang
    elif(oldAnn == 6):                  # old mm
        newAnn = 2                      # new mm
    elif(oldAnn == 7):                  # old rear
        newAnn = 4                      # new rear
    elif(oldAnn == 8):                  # old rest
        newAnn = 5                      # new rest
    elif(oldAnn == 9):                  # old walk
        newAnn = 6                      # new walk
    else:
        print('invalid ann: ', oldAnn)

    return newAnn

class DataReaderAV():
    '''
    Class to read video and annotation files together. 
    It uses PyAV and Pandas libraries to read the files and provides a simplified interface.
    '''
    
    #: the path to the video file being read
    videoFile: str
    
    #: the path to the annotation file being read
    annFile: str
    
    #: memory representation of the annotation data in Pandas format
    annData: pd.DataFrame
    
    #: reference to the PyAV object that provides the functionality to read video data
    avContainer: av.container.Container
    
    #: reference to the PyAV object corresponding to the video stream from which the frames are read
    videoStream = None
    
    #: the total number of frames in the selected video stream
    totalFrames: int
   
    #: shared logging handle 
    logger: Logger

    def __init__(self, logger, videoFilePath, annFilePath=None): 
        self.videoFile = videoFilePath
        self.annFile = annFilePath
        self.logger = logger
        
        self.avContainer = None
        self.videoStream = None
    
        self.annData = None

        # self.seekIndex = None
        self.totalFrames = 1
    
    
    def open(self, streamId = 0, offset = 0):
        '''
        Initializes the variables needed for the subsequent reading of the data.
        
        The video file in :data:`videoFile` will be accessible through :data:`avContainer`. The video stream identified through ``streamId`` will be accessible in :data:`videoStream`.
        
        If an annotation file was set in :data:`annFile`, the containing data is read into the :data:`annData` variable.
        
        :param streamId: the index of the video stream from which the frames will be read, defaults to 0
        :type streamId: int, optional
        :param offset: the frame position at which the first frame will be read, defaults to 0
        :type offset: int, optional
        :return: True when successfully opened both files, False otherwise
        :rtype: bool

        '''
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
        '''
        Reads up to ``n`` frames and their corresponding annotations starting from the first frame after the last one read, 
        or from the ``offset`` if this is the first call for this object.
        
        The frames returned are converted to single channel, and the top and bottom part are cropped out.
        The resulting content is converted to a square and scaled to 256*256 pixels. 
        
        
        Along with the visual data, the timestamp of the frame is also read from the video file. 
        This value represents the time that passed from the beginning of the recording, 
        and will typically be the encoding frame, unless the camera shutter time is 
        used at recording time.

        If annotation data is available, for each frame, the corresponding annotation from :data:`annData` is attached to the result.
        In this version of the software, we pack groom and micromovement together as mm+
        
        :param n: maximum number of frames to be read
        :type n: int
        :return: read and scaled frames, together with the corresponding frame number, timestamp and, if present, annotation
        :rtype: array

        '''
        result = []
        index = 0
        
        if(self.videoStream != None and index < n):
            # self.logger.log('read {} frames'.format(n), verbose)
            finished = False
            
            for packet in self.avContainer.demux(self.videoStream):
                if packet.size == 0:
                    # self.logger.log('demux empty packet', verbose)
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
                        crtRes.append(mapAnn(self.annData.loc[frame.index, 'annotation']))
                        
                    result.append(crtRes)
                    index += 1
                    
                    if index >= n:
                        finished = True
                        break
                if finished:
                    break
                
        return result

    # #TODO: 
    # def buildSeekIndex(self):
    #     self.logger.log('build seek index - not implemented', verbose)
    
    # def seek(self, n):
    #     if(self.seekIndex == None):
    #         self.buildSeekIndex()
        
    #     self.logger.log('seek frame {} - not implemented'.format(n), verbose)
        
if __name__ == '__main__':
    
    
    fullVideo = '/home/andrei/Videos/_originalRecordings/01_20180418_1200.mkv'
    fullAnnFile = '/home/andrei/Videos/_originalRecordings/ann_train/01_20180418_1200_RS.csv'
    
    shortVideo = '/home/andrei/Videos/_originalRecordings/x.mkv'
    vsv = '/home/andrei/Videos/tmp/pyAV/xs.mkv'
    videoFile = '/home/andrei/Videos/test/short_04_20180815_1200.mkv'
    
    logFile = '/home/andrei/Documents/GitHub/EthoProfiler/tmp/readerAV.log'
    log = Logger(logFile)
    
    dr = DataReaderAV(logger=log, videoFilePath=dsVid, annFilePath=dsAnn)
    if(dr.open()):
        print('test read')
        x = dr.readFrames(15)
        # print(x)
        # x = dr.readFrames(13)
        # print(x)
        
    
    
    
    
