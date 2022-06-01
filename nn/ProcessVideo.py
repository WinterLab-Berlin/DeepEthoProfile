#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 17:18:13 2022

@author: andrei
"""

import numpy as np
from EthoCNN import EthoCNN
import torch
from pandas import DataFrame

from DataReader import DataReader
from StackFrames import getTensors

class ProcessVideo():
    def __init__(self, modelPath, noClasses, videoFile, outputFile, segSize=125): 
        self.videoFile = videoFile
        self.outputFile = outputFile
        self.noClasses = noClasses
        self.modelPath = modelPath
        self.segSize = segSize
        
    def process(self, logger):
        # print('process video')
        self.model = EthoCNN(self.noClasses)
        self.model.load_state_dict(torch.load(self.modelPath))

        if torch.cuda.is_available():
           self.model.to(torch.device('cuda'))
                
        self.model.eval()

        reader = DataReader(self.videoFile)
        if(reader.openVideo() is False):
            print('cannot open video ', self.videoFile)
            logger.log('cannot open video {} '.format(self.videoFile))
            return -1

        t = 0        
        
        logger.log('processing results for video: {}\n'.format(self.videoFile))
        
        #write header
        resultsFile = open(self.outputFile, 'w')
        resultsFile.write('0:none; 1:drink; 2:eat; 3:groom back; 4:groom; 5:hang; 6:micromovement; 7:rear; 8:rest; 9:walk; \n')
        resultsFile.write('nnVersion:2\n')
        resultsFile.close()
        

        with torch.no_grad():
            while(True):
                # model.zero_grad()
                x = reader.getProcessingData(t * self.segSize + 1, self.segSize)
                if x is -1:
                    break

                xt,_ = getTensors(x)

            # Forward pass: Compute predicted y by passing x to the model
                crt_y = self.model(xt)
                npPred = crt_y.data.cpu().numpy()
            
                final_pred = np.argmax(npPred, axis=1)
            
                predex = np.zeros(self.segSize, dtype=np.int32)
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

                framesA = np.arange(t * self.segSize + 1, (t + 1) * self.segSize + 1, dtype=np.int32)
                padRes = np.stack((framesA, predex), axis=-1)
                predFrame = DataFrame(padRes)

                predFrame.to_csv(self.outputFile, sep=';', header=False, index=False, mode='a')

                # self.model.zero_grad(set_to_none=True)
                yield int((t * self.segSize * 100 + 1)/ reader.totalFrames)
            
                t = t + 1
                
        del reader
        del self.model  
            
        import gc
        gc.collect()
        torch.cuda.empty_cache()

        if(t > 0):
            print('finished processing video: ', self.videoFile)
        else:
            print('ERROR: something went wrong while processing video: ', self.videoFile)
            


if __name__ == "__main__":
    from Logger import Logger
    modelPath = './mouse_v2.model'
    videoFile = '/home/andrei/Videos/test/10_20180418_1800_s225000_n7500.avi'
    outputFile = '/home/andrei/Videos/test/10_20180418_1800_s225000_n7500.r2.csv'
    
    logPath = videoFile.replace('.avi', '_nn.log')
    # annFilePath = videoFilePath.replace('.avi', '.csv')
    
    logger = Logger(logPath)
    pc = ProcessVideo(modelPath, 10, videoFile, outputFile)
    
    try:
        crtStep = 0
        for x in pc.process(logger):
            crtStep = crtStep + 1
            if(crtStep % 10 == 0):
                mess = 'processing percent: {}'.format(x)
                logger.log(mess + '\n')
                
    except StopIteration:
        logger.log('finished at step {}'.format(crtStep))
        pass

