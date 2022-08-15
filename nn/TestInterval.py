#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 12:09:40 2021

@author: andrei
"""
import numpy as np
from EthoCNN import EthoCNN#, getTensors
import torch
from sklearn.metrics import accuracy_score

# from DataReader import DataReader
from DataReaderAV import DataReaderAV
from StackFrames import getTensors, getTestTensors


def setBNTrain(m):
   if isinstance(m, torch.nn.BatchNorm2d) or isinstance(m, torch.nn.BatchNorm1d) or isinstance(m, torch.nn.LSTM):
      m.train()
      
def setDropEval(m):
   if isinstance(m, torch.nn.Dropout2d):
      m.eval()


class TestInterval():
    def __init__(self, path, noClasses, videoFile, annFile, logger): #posFile, 
        self.videoFile = videoFile
        self.annFile = annFile
        # self.posFile = posFile
        
        #self.model = model
        
        self.segSize = 125
        
        self.noClasses = noClasses
        self.path = path
        
        self.logger = logger
            
        
    def test(self):
        # print('test interval')
        self.model = EthoCNN(self.noClasses)
            
        self.model.load_state_dict(torch.load(self.path))

        if torch.cuda.is_available():
           self.model.to(torch.device('cuda'))
                
        self.model.eval()
        # for m in self.model.modules():
        #     if isinstance(m, torch.nn.Dropout2d) or isinstance(m, torch.nn.Dropout):
        #         m.eval()
            
        sumScore = 0
    
    #TODO: reset dinamic values
    
        reader = DataReaderAV(self.logger, self.videoFile, self.annFile) 
        if(reader.open() is False):
            print('cannot open video ', self.videoFile)
            return -1
        confusion = np.zeros((self.noClasses, self.noClasses))
        t = 0        
        #self.model.resetHidden()
        with torch.no_grad():
            while(True):
                # model.zero_grad()
                dataSegment = reader.readFrames(self.segSize)
                if(len(dataSegment) == 0):
                    break
                
                data = np.array(dataSegment, dtype=object)
                x = data[:, 2]
                y = data[:, 3].tolist()

                # x = data[:][2]
                # y = data[:][3]
                
                xt = getTestTensors(x)

            # Forward pass: Compute predicted y by passing x to the model
                crt_y = self.model(xt)
                npPred = crt_y.data.cpu().numpy()
            
                final_pred = np.argmax(npPred, axis=1)
            
                predex = np.zeros(self.segSize)
                bins = int((self.segSize-5)/6)
                
                predex[0] = final_pred[0]
                predex[1] = final_pred[0]
                predex[2] = final_pred[0]
                for i in range(bins):
                    ii = i * 6 + 5
                    predex[ii-3] = final_pred[i]
                    predex[ii-2] = final_pred[i]
                    predex[ii-1] = final_pred[i]
                    predex[ii] = final_pred[i]
                    predex[ii+1] = final_pred[i]
                    predex[ii+2] = final_pred[i]
                    predex[ii+3] = final_pred[i]
                predex[-3] = final_pred[-1]
                predex[-2] = final_pred[-1]
                predex[-1] = final_pred[-1]
                    
                # ann = yt.data.cpu().numpy()
                score = accuracy_score(y, predex)

                for i in range(len(y)):
                    confusion[y[i], int(predex[i])] += 1
            
                sumScore = sumScore + score
            
                t = t + 1
                # resetModel = False
                
        del reader
        del self.model  
            
        import gc
        gc.collect()
        torch.cuda.empty_cache()

        # if i % 2 == 0:
        if(t > 0):
            print('tested video: ', self.videoFile, ', avg sumScore = ', sumScore/t)
            return sumScore/t, confusion
        else:
            print('ERROR: something went wrong while processing video: ', self.videoFile)
            return 0
            


