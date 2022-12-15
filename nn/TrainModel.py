#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The TrainModel class 


@author: Andrei Istudor     andrei.istudor@hu-berlin.de
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
from Logger import Logger
from TestModel import TestModel

noClasses = 10

class TrainModel():
    '''
    Class to train a new model using a set of annotated video intervals. 
    '''
    
    #: the list of :class:`TrainInterval` objects that form an epoch
    trainIntervals: []

    #: the model that will be trained
    model: EthoCNN
    
    #: number of classes the model is initialized with
    noClasses: int

    #: the handle to the optimizer used for updating the model's parameters
    optimizer: torch.optim.Optimizer
    
    #: the handle to the loss class used for computing the lost gradients
    criterion: torch.nn.CrossEntropyLoss
    
    #: counts the number of iterations where the average cost is under a certain threshold
    stagnating: int
    
    #: simple logger used mostly for debugging
    logger: Logger
    
    def __init__(self, noClasses, log):
        print('init TrainModel')
        #TODO: init model 
        self.model = None
        self.trainIntervals = []
        
        self.running = False
        
        self.noClasses = noClasses
        self.initModel()
        
        self.stagnating = 0
        
        self.logger = log
        
    def initModel(self):
        '''
        Initializes the :data:`model`, the :data:`optimizer` and the :data:`criterion`.
        
        If cuda is available, they will all be transfered to the GPU memory.

        '''
        self.model = EthoCNN(self.noClasses)
        self.model.train()       
        # optimizer = torch.optim.Adam(model.parameters(), lr=0.07)
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr = 1e-2)
        self.criterion = torch.nn.CrossEntropyLoss()
        
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            self.criterion = self.criterion.cuda()


    def addTrainInterval(self, videoFile, annFile): 
        '''
        Creates a new :class:`TrainInterval` object and adds it to 
        the list in :data:`trainIntervals`. This will use the video found at `videoFile`
        and the annotation file found at `annFile` path.
        
        :param videoFile: path to the video file to be used for training
        :type videoFile: str
        :param annFile: path to the annotation file to be used as target
        :type annFile: str
        '''
        newTrainInterval = TrainInterval(self.model, self.optimizer, self.criterion, videoFile, annFile, self.noClasses, logger=self.logger) 
        self.trainIntervals.append(newTrainInterval)
        
        
    def trainFullStep(self):
        '''
        Train an epoch. 
        
        Calls the :func:`TrainInterval.TrainInterval.train` for all the items added in :data:`trainIntervals`.
        The average cost, the used target annotaions, the training accuracy score and the corresponding confusion matrix
        are accumulated and displayed.
        
        :return: average cost
        :rtype: float

        '''
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
                cost, annSet, acc, cc = i.train()

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
            
    def train(self, epochs):
        '''
        Trains the model at :data:`model` for a specified number of epochs. 
        All but the first the intermediate models are saved.
        
        The process might stop before if the average cost persists under a cetrain threshold for more then 5 steps.
        
        :param epochs: the numer of epochs that will be trained
        :type epochs: int

        '''
        self.running = True
        minCost = -1
        self.stagnating = 0
        
        # shuffle(self.trainIntervals)
        
        for i in range(epochs):
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
                        self.stagnating = 0
                    else:
                        if(self.stagnating < 5):
                            print('stagnating: {}, crt min still is {}'.format(self.stagnating, minCost))
                            self.stagnating += 1
                            # print('updated minCost because of videos (possibly) removed, previously={}'.format(minCost))
                            # minCost = avgCost
                        else:
                            print('cost grew/stagnated, stopping at {}'.format(minCost))
                            self.running = False
            else:
                break
            
            

    # #TODO: this should be called async
    # def stop(self):
    #     self.running = False
        
    def saveModel(self, path):
        '''
        Saves the current model at the specified path.
        
        :param path: path to the file where the model will be saved
        :type path: str

        '''
        torch.save(self.model.state_dict(), path)
        
    def loadModel(self, path):
        '''
        Creates a new :class:`EthoCNN.EthoCNN` instance with :data:`noClasses` outputs and 
        loads into it the state dictionary from the specified path. 
        
        :param path: path to the file where the model is found
        :type path: str

        '''
        self.model = EthoCNN(self.noClasses)
        
        self.model.load_state_dict(torch.load(path))

        if torch.cuda.is_available():
            self.model.to(torch.device('cuda'))
            

    def cleanup(self):
        '''
        Deletes the :data:`model`, the :data:`optimizer` and the :data:`criterion` and calls system cleanup functions.
    
        '''
        del self.model  
        del self.optimizer
        del self.criterion
            
        import gc
        gc.collect()
        torch.cuda.empty_cache()
    
        

if __name__ == "__main__":
    import sys
    
    # trainVideoPath = '/home/andrei/Videos/2205_trainCropVideos_21/'
    trainVideoPath = ''
    
    if (len(sys.argv) > 1):
        # global trainVideoPath
        print('training folder: ', sys.argv[1])
        trainVideoPath = sys.argv[1]
    else:
        print ('not enough parameters')
        exit(1)
    
    log = Logger('train.log')

    # modelPath = './mouse.modular.model'
    
    epochs = 13
    
    # #train
    # trainModel = TrainModel(noClasses, log)
    
    # for videoFile in glob.glob(trainVideoPath + '*.avi'):
    #     annFile = videoFile.replace('.avi', '_ann.csv')
    #     if(path.exists(annFile)): 
    #         trainModel.addTrainInterval(videoFile, annFile)
    #     else:
    #         print('missing data for file ', videoFile)


    # trainModel.train(epochs)
    # #trainModel.saveModel(modelPath)
    # trainModel.cleanup()
    # del trainModel
    
    
    #test    
    dataFolder = ''
    
    if(len(sys.argv) > 2):
        dataFolder = sys.argv[2]
        print('test videos folder: ', sys.argv[2])
        if(len(sys.argv) > 3):
            annFolder = sys.argv[3]
        else:
            annFolder = dataFolder + '/ann_train'
        print('test annotations folder: ', annFolder)
        
        
        # for x in range(4, epochs):#epochs-10):
        modelName = 'mouse_v2.model' 
        # modelName = 'step_{}.model'.format(x)#epochs - x)
        print(' - - - testing model: {} - - - '.format( modelName))
        testModel = TestModel(noClasses, modelName, log)
        
        for crtVideo in glob.glob(dataFolder + '*.avi'):
            crtAnn = crtVideo.replace('.avi', '.csv')
            if(path.exists(crtAnn)): 
                testModel.addTestInterval(crtVideo, crtAnn)
            else:
                print('missing data for file ', crtVideo)
                
        print('added test files')
        testModel.test()
        del testModel
    else:
        print('no testing data')
        
    
        
