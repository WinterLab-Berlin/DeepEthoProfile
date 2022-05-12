#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 12:54:41 2021

@author: andrei
"""
import torch
import torch.nn
import torch.optim
from torch.autograd import Variable
from random import randint

import numpy as np
from os import path
# from pathlib import Path
import glob
from random import shuffle

from EthoCNN import EthoCNN
from TrainInterval import TrainInterval
# from TestInterval import TestInterval
from Logger import Logger
from VideoHelper import cutTrainingSegment
from SelectTrainingData import selectTrainIntervals, getOriginalFiles_PCRS, cutOiginalTrainingSegment
from TestModel import TestModel

noClasses = 10

class TrainModel():
    def __init__(self, noClasses):
        print('init TrainModel')
        #TODO: init model 
        self.model = None
        self.trainIntervals = []
        
        self.running = False
        self.stopping = False
        
        self.noClasses = noClasses
        self.initModel()
        
        self.stag = 0
        self.trainRemoveThresh = 0.001
        
    def initModel(self):
        self.model = EthoCNN(self.noClasses)
        self.model.train()       
        # optimizer = torch.optim.Adam(model.parameters(), lr=0.07)
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr = 1e-2)
        self.criterion = torch.nn.CrossEntropyLoss()
        
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            self.criterion = self.criterion.cuda()


    def cleanup(self):

        del self.model  
        del self.optimizer
        del self.criterion
            
        import gc
        gc.collect()
        torch.cuda.empty_cache()

    def addTrainInterval(self, videoFile, annFile): 
        newTrainInterval = TrainInterval(self.model, self.optimizer, self.criterion, videoFile, annFile, self.noClasses) 
        self.trainIntervals.append(newTrainInterval)
        
        
    def trainFullStep(self, step):
        ti = 0
        tc = 0
        ta = 0
        confusion = np.zeros((self.noClasses, self.noClasses))

        annTotalSet = np.zeros(self.noClasses)
        
        lt = len(self.trainIntervals)
        if(lt < 10):
            print('too few training videos, skip')
            return 0
        for i in self.trainIntervals:

            if(self.running):
                cost, annSet, acc, cc = i.train(annTotalSet)

                tc = tc + cost
                ti = ti + 1
                ta += acc
                annTotalSet = annTotalSet + annSet
                confusion += cc

                if(ti%10 == 0):
                    print(' = step {}, cost={}, avg acc={}'.format(ti, tc/ti, ta/ti))
            else:
                break
        print(' = = = for this full step, annTotalSet = ', np.uint32(annTotalSet))
        print('train acc so far (with dropout) = {}'.format(ta / ti))
        with np.printoptions(suppress=True):
            print('confusion: \n', confusion)
            

        if(ti > 0):
           return tc/ti
        else:
           return 0
            
    def train(self, steps):
        self.running = True
        # stag = 0
        minCost = -1
        self.stag = 0
        for i in range(steps):
            print('train step ', i)
            if(self.running):
                shuffle(self.trainIntervals)
                
                avgCost = self.trainFullStep(i)
                print('FULL STEP! avg cost is: ', avgCost)
                
                if(i > 0):
                    self.saveModel('step_{}.model'.format(i))
                if(minCost <= 0):
                    minCost = avgCost
                else:
                    if(minCost - avgCost > 0.001):
                        print('updated minCost, previously={}'.format(minCost))
                        minCost = avgCost
                        self.stag = 0
                    else:
                        if(self.stag < 5):
                            print('stagnating: {}, crt min still is {}'.format(self.stag, minCost))
                            self.stag += 1
                            # print('updated minCost because of videos (possibly) removed, previously={}'.format(minCost))
                            # minCost = avgCost
                        else:
                            print('cost grew/stagnated, stopping at {}'.format(minCost))
                            self.running = False
            else:
                break
            
            

    #TODO: this should be called async
    def stop(self):
        self.running = False
        
    def saveModel(self, path):
        torch.save(self.model.state_dict(), path)
        
    def loadModel(self, path):
        self.model = EthoCNN(self.noClasses)
        
        self.model.load_state_dict(torch.load(path))

        if torch.cuda.is_available():
            self.model.to(torch.device('cuda'))
            

        

if __name__ == "__main__":
    import sys
    
    trainVideoPath = '' #/home/andrei/Videos/train_orig/'
    
    if (len(sys.argv) > 1):
        # global trainVideoPath
        print('training folder: ', sys.argv[1])
        trainVideoPath = sys.argv[1]
    else:
        print ('not enough parameters')
        exit(1)


    modelPath = './mouse.modular.model'
    
    epochs = 3
    
    #train
    trainModel = TrainModel(noClasses)
    
    for videoFile in glob.glob(trainVideoPath + '*.avi'):
        annFile = videoFile.replace('.avi', '_ann.csv')
        if(path.exists(annFile)): 
            trainModel.addTrainInterval(videoFile, annFile)
        else:
            print('missing data for file ', videoFile)


    trainModel.train(epochs)
    trainModel.saveModel(modelPath)
    trainModel.cleanup()
    del trainModel
    
    
    #test    
    dataFolder = ''#'/home/andrei/Videos/orig_work'
    annFolder = ''#'/home/andrei/Videos/orig_work/ann_train'
    
    if(len(sys.argv) > 2):
        dataFolder = sys.argv[2]
        print('test videos folder: ', sys.argv[2])
        if(len(sys.argv) > 3):
            annFolder = sys.argv[3]
        else:
            annFolder = dataFolder + '/ann_train'
        print('test annotations folder: ', annFolder)
        
        intervals_PCRS = [[0, 7500], [45000, 52500], [90000, 97500], [135000, 142500], [180000, 187500], [225000, 232500],
                          [270000, 277500], [315000, 322500], [360000, 367500], [405000, 412500], [450000, 457500], [495000, 502500]]
        # intervals_RS = [[1, 7500], [270000, 277500]]
        
        inputFiles = getOriginalFiles_PCRS(dataFolder, annFolder)
        
        for x in range(2, epochs):#epochs-10):
            modelName = 'step_{}.model'.format(x)#epochs - x)
            print(' - - - testing model: {} - - - '.format( modelName))
            testModel = TestModel(noClasses, modelName)
            
            for x in inputFiles:
                for crtInt in intervals_PCRS:
                    segVideo, segAnn = cutOiginalTrainingSegment(x[0], x[1], crtInt[0], crtInt[1] - crtInt[0])
                    testModel.addTestInterval(segVideo, segAnn) #segPos, 
                    
            
            testModel.test()
            del testModel
    else:
        print('no testing data')
        
    
        
