#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 12:48:13 2021

@author: andrei
"""
import numpy as np
import pandas as pd
import torch

from random import randint

from DataReader import DataReader
from sklearn.metrics import accuracy_score
from StackFrames import getTensors

class TrainInterval():
    def __init__(self, model, optimizer, criterion, videoFile, annFile, noClasses): #posFile, 
        self.videoFile = videoFile
        self.annFile = annFile
        # self.posFile = posFile
        
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.noClasses = noClasses
        
        self.segSize = 41
        
    
    def train(self, prevAnn = [], balanceThresh = 1000):
        # print('train video: {}, {}, {}'.format(self.videoFile, self.posFile, self.annFile))
        
        loss = 0
        avg_cost = 0

        startIndex = randint(0,11)
        # stopIndex = -1
        
        # if max(prevAnn) > balanceThresh * 10:
        #     startIndex, stopIndex = self.balanceAnn(prevAnn, balanceThresh)
        
        if(startIndex < 0):
            print('skipping this video now: ', self.videoFile)
            return -1, np.zeros(self.noClasses)
        
        reader = DataReader(self.videoFile, self.annFile) #self.posFile, 
        if(reader.openVideo() is False):
            print('cannot open video ', self.videoFile)
            return -1, np.zeros(self.noClasses)
        
        # print('initialized reader..')

        t = 0
        noFrames = 0
        annSet = np.zeros(self.noClasses)
        # self.model.resetHidden()

        confusion = np.zeros((self.noClasses, self.noClasses))

        while True:
            # if(stopIndex > 0 and startIndex + (t+1) * self.segSize > stopIndex):
            #     break
            
            # x, pos, y = reader.getTrainingData(startIndex + t * self.segSize + 1, self.segSize)
            x, y = reader.getTrainingData(startIndex + t * self.segSize + 1, self.segSize)
            if x is -1:
                break
            
            # xt, posT, yt = self.model.getTensors(x, pos, y)
            # xt, yt = self.model.getTensors(x, y, modify=True)
            xt, yt = getTensors(x, y, modify=True)
            
            # model.zero_grad()
            self.optimizer.zero_grad()
            # Forward pass: Compute predicted y by passing x to the model
            crt_y = self.model(xt) #, posT
            
            # resetRNN = False
        
            # Compute and print loss
            loss = self.criterion(crt_y, yt)
        
            # Zero gradients, perform a backward pass, and update the weights.
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
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

            ann = yt.data.cpu().numpy()
            for x in ann:
                annSet[x] = annSet[x] + 1
            
        del reader
        
        if(noFrames > 0):
            # print('trained video: ', self.videoFile, ', avg= ', avg_cost/noFrames)
            return avg_cost/noFrames, annSet, score, confusion
        else:
            print(' - - skipped training video: ', self.videoFile)
            return -1, annSet, score, confusion
            
