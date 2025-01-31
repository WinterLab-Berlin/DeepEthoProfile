#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 11:03:08 2022

@author: Andrei Istudor     andrei.istudor@gmail.com
"""

import av
import pandas as pd
import numpy as np
import cv2
# from skimage.transform import resize
import logging

from Logger import Logger

# logging.basicConfig()
# logging.getLogger("libav").setLevel(logging.FATAL)
# av.logging.set_level(logging.FATAL)
av.logging.set_level(av.logging.PANIC)

verbose = False

# def mapAnn(oldAnn):
#     newAnn = 2
    
#     if(oldAnn == 1):                    # old drink
#         newAnn = 0                      # new drink
#     elif(oldAnn == 2):                  # old eat
#         newAnn = 1                      # new eat
#     elif(oldAnn == 4):                  # old groom 
#         newAnn = 2                      # new mm
#     elif(oldAnn == 5):                  # old hang
#         newAnn = 3                      # new hang
#     elif(oldAnn == 6):                  # old mm
#         newAnn = 2                      # new mm
#     elif(oldAnn == 7):                  # old rear
#         newAnn = 4                      # new rear
#     elif(oldAnn == 8):                  # old rest
#         newAnn = 5                      # new rest
#     elif(oldAnn == 9):                  # old walk
#         newAnn = 6                      # new walk
#     else:
#         # print('invalid ann: ', oldAnn)
#         newAnn = 2

#     return newAnn

# def mapAnn2(oldAnn):
#     newAnn = 2
    
#     if(oldAnn == 1):                    # old drink
#         newAnn = 0                      # new drink
#     elif(oldAnn == 2):                  # old eat
#         newAnn = 1                      # new eat
#     elif(oldAnn == 3):                  # old groom back
#         newAnn = 2                      # new groom
#     elif(oldAnn == 4):                  # old groom 
#         newAnn = 2                      # new groom
#     elif(oldAnn == 5):                  # old hang
#         newAnn = 3                      # new hang
#     elif(oldAnn == 6):                  # old mm
#         newAnn = 4                      # new mm
#     elif(oldAnn == 7):                  # old rear
#         newAnn = 5                      # new rear
#     elif(oldAnn == 8):                  # old rest
#         newAnn = 6                      # new rest
#     elif(oldAnn == 9):                  # old walk
#         newAnn = 7                      # new walk
#     else:
#         # print('invalid ann: ', oldAnn)
#         newAnn = 2 #defaults to mm

#     return newAnn

maxV = 170
minV = 10

# Make a LUT (Look-Up Table) to translate image values
LUT=np.zeros(256, dtype=np.uint8)
LUT[minV:maxV+1] = np.linspace(start=0, stop=255, num=(maxV-minV)+1, endpoint=True, dtype=np.uint8)
LUT[maxV+1:] = 255


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
   
    #: simple shared logger used mostly for debugging
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
        self.start = 0
        self.crtFrame = 0
        self.ended = True
    
    
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

            self.videoStream = self.avContainer.streams.video[0]
            self.crtFrame = 0
            self.totalFrames = 5000
            self.ended = False
            if(self.avContainer.streams.video[streamId].duration):
                self.totalFrames = (self.avContainer.streams.video[streamId].duration +1 )/ 40
            
            if (self.annFile is not None):
                self.annData = pd.read_csv(self.annFile, sep=';', header=1)
                
            self.start = offset
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
        
    def close(self):
        if (self.annData is not None):
            del self.annData
        if(self.avContainer is not None):
            self.avContainer.close()
            del self.avContainer
        self.crtFrame = 0
        self.ended = True
        
        
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
        fi = 0
        finished = False
        
        while(self.videoStream != None and not finished and not self.ended):
            # self.logger.log('read {} frames'.format(n))
            
            for packet in self.avContainer.demux(self.videoStream):
                if packet.size == 0:
                    # print('demux empty packet')
                    finished = True
                    break
                for frame in packet.decode():
                    crtVFrame = frame.to_ndarray(format='gray')
                    if(self.start > 0):
                        self.start -= 1
                        continue

                    h, w = crtVFrame.shape
                    if (h != 256 or w != 256):
                        crtVFrame = crtVFrame[90:440, :]
                        crtVFrame = cv2.copyMakeBorder(crtVFrame, 177, 177, 0, 0, cv2.BORDER_CONSTANT, None, 0)
                        crtVFrame = cv2.resize(crtVFrame, (256, 256)) 


                    crtRes = [self.crtFrame, frame.pts, LUT[crtVFrame]]

                    #add annotation
                    if(self.annData is not None):
                        if(self.crtFrame >= self.annData.shape[0]):
                            print('=== no more annotations available for frame {}, ann size={}'.
                                  format(self.crtFrame, self.annData.shape[0]))
                            finished = True
                            self.ended = True
                            break
                        else:
                            # print('read')
                            crtRes.append(int(self.annData.loc[self.crtFrame, 'annotation']))
                    else:
                        crtRes.append(0)
                        
                    result.append(crtRes)
                    self.crtFrame += 1

                    index += 1
                    
                    if index >= n:
                        # print('yield step', index)
                        index = 0
                        yield result
                        # return result
                        result = []
                if(self.ended):
                    break
                
            # print('yield rest ', len(result))
            index = 0
            yield(result)
            finished = True
            # return result
        # print('read {} frames, now at index {}'.format(n, fi))
                
        # return result

    # #TODO: 
    # def buildSeekIndex(self):
    #     self.logger.log('build seek index - not implemented', verbose)
    
    # def seek(self, n):
    #     if(self.seekIndex == None):
    #         self.buildSeekIndex()
        
    #     self.logger.log('seek frame {} - not implemented'.format(n), verbose)
        

    
    
    
