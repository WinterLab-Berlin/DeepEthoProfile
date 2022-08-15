#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 11:26:07 2021

@author: andrei
"""
# from EthoCNN import EthoCNN
from TestInterval import TestInterval

import torch
import numpy as np


class TestModel:
    def __init__(self, noClasses, path, logger):
        with torch.no_grad():
            self.model = None
            self.testIntervals = []
            
            self.running = False
            self.stopping = False
            
            self.path = path
            self.noClasses = noClasses
            
            self.logger = logger
                          
    def addTestInterval(self, videoFile, annFile): #posFile, 
        newTrainInterval = TestInterval(self.path, self.noClasses, videoFile, annFile, self.logger) #posFile, 
        self.testIntervals.append(newTrainInterval)
        
    def test(self):
        self.running = True
        ta = 0
        ti = 0
        confusion = np.zeros((self.noClasses, self.noClasses))
        #with torch.no_grad():
        for i in self.testIntervals:
            if(self.running):
                ca, cc = i.test()
                ta = ta + ca
                confusion += cc
                ti = ti + 1
            else:
                break

            if(ti%10==1):
                print('cummulated test result at step {} is {} '.format(ti, ta/ti))
                # with np.printoptions(suppress=True):
                #     print('confusion: \n', confusion)
        print('final test result = ', ta/ti)
        with np.printoptions(suppress=True):
            print('confusion: \n', confusion)
