#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 12:48:13 2021

@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""
import numpy as np
import pandas as pd
import torch

from random import randint, random

from EthoCNN import EthoCNN
from DataReaderAV import DataReaderAV
from sklearn.metrics import accuracy_score
from StackFrames import getTensors
from Logger import Logger

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
        
    
    def train(self, model, optimizer, criterion, logger, epoch):
        '''
        Trains the model at :data:`model` with the frames from :data:`videoFile` against the target in :data:`annFile`

        The process is split into steps of maximum :data:`segSize` frames.
        The classification is done with a stride of 8, as described in :func:`StackFrames.getTensors`. 
        For each step, the predicted annotations are computed, then the loss gradients against the target from the manual annotation. 
        The :data:`optimizer` then updates the model parameters. 
        
        :return: the average training cost, the set of target annotations used, the training accuracy score and the corresponding confusion matrix
        :rtype: float, [], float, []

        '''
        # print('train video: {}, {}, {}'.format(self.videoFile, self.posFile, self.annFile))
        mult = 1
        if(epoch > 0):
            mult += (epoch)/80 #100, 50, 70
        skip = False
        #something very special for the MIT clipped db
        crtVid = self.videoFile
        if(crtVid.find('_d_') > 0 or crtVid.find('_drink_') > 0):
            # if(random() < 0.01 * mult):
            #     skip = True
            pass
        elif(crtVid.find('_e_') > 0 or crtVid.find('_eat_') > 0):
            if(random() < 0.65 * mult): #0.55 0.6
                skip = True
        elif(crtVid.find('_g_') > 0 or crtVid.find('_groom_') > 0):
            if(random() < 0.85 * mult): #0.82
                skip = True
        elif(crtVid.find('_gb_') > 0 or crtVid.find('_groomback_') > 0):
            if(random() < 0.75 * mult): #0.75
                skip = True
        elif(crtVid.find('_ha_') > 0 or crtVid.find('_hang_') > 0):
            if(random() < 0.7 * mult): #0.65
                skip = True
        elif(crtVid.find('_he_') > 0 or crtVid.find('_head_') > 0 ):
            if(random() < 0.1 * mult): #0.02
                skip = True
            pass
        elif(crtVid.find('_r_') > 0 or crtVid.find('_rear_') > 0):
            if(random() < 0.4 * mult): #0.28 0.35
                skip = True
        elif(crtVid.find('_rs_') > 0 or crtVid.find('_rest_') > 0):
            if(random() < 0.8 * mult): #0.78
                skip = True
        elif(crtVid.find('_w_') > 0 or crtVid.find('_walk_') > 0):
            if(random() < 0.05 * mult): #0.01
                skip = True
            pass
        
        
        loss = 0
        avg_cost = 0
        score = 0
        
        annSet = np.zeros(self.noClasses)
        # self.model.resetHidden()

        confusion = np.zeros((self.noClasses, self.noClasses))
        

        startIndex = randint(0, 3)
        # stopIndex = -1
        
        if(skip):
            # print(' - - - - - - skipping this video now: ', self.videoFile)
            return -1, annSet, 0, confusion
        
        reader = DataReaderAV(logger, self.videoFile, self.annFile) #self.posFile, 
        if(reader.open(offset=startIndex) is False):
            print('cannot open video ', self.videoFile)
            return -1, np.zeros(self.noClasses)
        
        # print('initialized reader..')

        t = 0
        noFrames = 0
        annSet = np.zeros(self.noClasses)
        # self.model.resetHidden()

        for dataSegment in reader.readFrames(self.segSize):
            if(len(dataSegment) < 12): #self.segSize):
                # print('read too few frames ', len(dataSegment))
                break

            data = np.array(dataSegment, dtype=object)
            x = data[:, 2]
            y = data[:, 3]
            xt, yt = getTensors(x, y, modify=True)
            
            # model.zero_grad()
            optimizer.zero_grad()

            # compute predicted annotations by passing the stacked images to the model
            crt_y = model(xt) #, posT
            
            # Compute loss
            loss = criterion(crt_y, yt)
        
            # Zero gradients, perform a backward pass, and update the weights.
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if(np.isnan(loss.item())):
                print('loss is NaN for: ', self.videoFile, ', cost= ', avg_cost, ', step', t)
            else:
                avg_cost = avg_cost + loss.item()

#debug/status data:
                npPred = crt_y.data.cpu().numpy()
                final_pred = np.argmax(npPred, axis=1)
                ann = yt.data.cpu().numpy()
                score = accuracy_score(ann, final_pred)
                for i in range(len(ann)):
                    confusion[ann[i], final_pred[i]] += 1
    
                t = t + 1
                noFrames = noFrames + self.segSize
    
                for x in ann:
                    annSet[x] = annSet[x] + 1
            
        reader.close()
        del reader
        
        if(t > 0):
            # print('trained video: ', self.videoFile, ', avg= ', avg_cost/noFrames, ', cost= ', avg_cost)
            return avg_cost/t, annSet, score/t, confusion
        else:
            # print(' - - skipped training video: ', self.videoFile)
            return -1, annSet, 0, confusion
            
