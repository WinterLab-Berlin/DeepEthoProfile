#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""
# from EthoCNN import EthoCNN
from TestInterval import TestInterval
from Logger import Logger

import torch
import numpy as np


class TestModel:
    '''
    Class for testing the model found at :data:`modelPath` with :data:`noClasses` outputs.
    
    '''
    
    #: path to the saved model that will be tested
    modelPath: str
    
    #: number of classes the model is initialized with
    noClasses: int
    
    #: the list of TestInterval objects
    testIntervals: []
    
    #: simple logger used mostly for debugging
    logger: Logger
    
    def __init__(self, noClasses, modelPath, logger):
        self.testIntervals = []
        
        self.running = False
        
        self.modelPath = modelPath
        self.noClasses = noClasses
        
        self.logger = logger
                          
    def addTestInterval(self, videoFile, annFile): 
        '''
        Creates a new :class:`TestInterval.TestInterval` object and adds it to 
        the list in :data:`testIntervals`. This will use the video found at `videoFile`
        and the annotation file found at `annFile` path.
        
        :param videoFile: path to the video file to be tested
        :type videoFile: str
        :param annFile: path to the annotation file to be used
        :type annFile: str

        '''
        newTrainInterval = TestInterval(self.modelPath, self.noClasses, videoFile, annFile, self.logger) #posFile, 
        self.testIntervals.append(newTrainInterval)
        
    def test(self):
        '''
        Calls the :func:`TestInterval.TestInterval.test` method for all the objects in :data:`testIntervals`.
        The results are accumulated and the final accuracy and confusion matrix are
        displayed at the end. 
        
        Intermediate accuracy results are also displayed to follow the progress.
        '''
        self.running = True
        ta = 0
        ti = 0
        confusion = np.zeros((self.noClasses, self.noClasses))
        
        
        with torch.no_grad():
            # print('test {} intervals'.format(len(self.testIntervals)))
            for crtInt in self.testIntervals:
                annList = np.zeros(self.noClasses, dtype=int)
                predList = np.zeros(self.noClasses, dtype=int)
                if(self.running):
                    ca, cc = crtInt.test()
                    if(ca >= 0):
                        ta = ta + ca
                        confusion += cc
                        ti = ti + 1
                        
                        # tpC = 0
                        # taC = 0
                        # for i in range(len(confusion)):
                        #     for j in range(len(confusion[i])):
                        #         annList[i] += cc[i, j]
                        #         predList[j] += cc[i, j]
                        #         taC += cc[i, j]
                        #         if(i == j):
                        #             tpC += cc[i, j]
                                    
                        # print(' test video {} - - - ACC = {}'.format(crtInt.videoFile, tpC/taC))
                        # with np.printoptions(suppress=True):
                        #     print('annotations: \n', annList)
                        #     print('predictions: \n', predList)
                        #         print('predictions: \t', predList)
                else:
                    break
                
                if(ti%10 == 0):
                    tpC = 0
                    taC = 0
                    for i in range(len(confusion)):
                        for j in range(len(confusion[i])):
                            taC += confusion[i, j]
                            if(i == j):
                                tpC += confusion[i, j]
                    # print(' = interval {}, cost={}, avg acc={}, last acc = {}'.format(ti, tc/ti, ta/ti, acc))
                    print(' = interval {} - - - ACC = {:.2%}'.format(ti, tpC/taC))
                    # with np.printoptions(suppress=True):
                    #     print('confusion: \n', confusion)


        print('final test result = ', ta/ti)
        with np.printoptions(suppress=True):
            print('confusion: \n', confusion)
