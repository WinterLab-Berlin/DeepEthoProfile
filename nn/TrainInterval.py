#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 12:48:13 2021

@author: Andrei Istudor     andrei.istudor@gmail.com
"""
import numpy as np
import pandas as pd
import torch

from random import randint, random

from EthoCNN import EthoCNN
from DataReaderAV import DataReaderAV
from sklearn.metrics import accuracy_score
# from StackFrames import getTensors
from Logger import Logger
from FrameSelect import FrameSelect

class TrainInterval():
    '''
    Class to train a model with one annotated video interval. 
    '''

    #: the path to the video file to be used for training
    videoFile: str
    
    #: the path to the file containing the groundtruth for the video
    annFile: str

    # #: the handle to the model used for training
    # model: EthoCNN
    
    #: number of outputs for the current model
    noClasses: int
    
    # #: the handle to the optimizer used for updating the model's parameters
    # optimizer: torch.optim.Optimizer
    
    # #: the handle to the loss class used for computing the lost gradients
    # criterion: torch.nn.CrossEntropyLoss
    
    #: the maximum number of frames that will be processed in parallel
    segSize: int
    
    # #: simple logger used mostly for debugging
    # logger: Logger

    def __init__(self, model, optimizer, criterion, videoFile, annFile, noClasses, logger): #posFile, 
        self.videoFile = videoFile
        self.annFile = annFile
        
        # self.model = model
        # self.optimizer = optimizer
        # self.criterion = criterion
        self.noClasses = noClasses
        
        self.segSize = 144 #53
        # self.logger = logger
        self.fs = None
        self.noSets = 0
        self.annRes = np.zeros(noClasses, dtype=int)

        
    
    def startNew(self, logger):
        startIndex = randint(0, 11)
        
        if(self.fs != None):
            self.fs.stopReader()
            self.fs = None
            
        self.annRes = np.zeros(self.noClasses, dtype=int)
        self.fs = FrameSelect(logger, self.videoFile, self.annFile, startIndex)
        self.fs.startReader()
    
    def getNextStackedImage(self, logger):
        # maxAnn = [199, 20, 20, 199, 15, 18, 40, 99]
        # maxAnn = [199, 40, 40, 199, 30, 20, 40, 199]

        # maxAnn = [199, 30, 30, 199, 25, 28, 40, 199]
        
        if(self.fs != None):
            imS, annS, finished = self.fs.getTrainTuple()
        
            if(finished):
                self.fs.stopReader()
                self.fs = None
        #         imS, annS, finished = self.fs.getTrainTuple()
            
            return imS, annS, finished
        else:
            return None, None, True


