#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
the TestInterval class

@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""
import numpy as np
from EthoCNN import EthoCNN#, getTensors
import torch
from sklearn.metrics import accuracy_score

# from DataReader import DataReader
from DataReaderAV import DataReaderAV, mapAnn
from StackFrames import getTensors, getTestTensors
from Logger import Logger


class TestInterval():
    '''
    Class for testing a saved model against a video file and the associated annotation file.
    '''

    #: path to the saved model that will be tested
    modelPath: str
    
    #: number of classes the model is initialized with
    noClasses: int
    
    #: path to the video file that will be used
    videoFile: str
    
    #: path to the annotation file that will be used
    annFile: str
    
    #: the maximum number of frames that will be processed in parallel
    segSize: int
    
    #: simple logger used mostly for debugging
    logger: Logger

    def __init__(self, modelPath, noClasses, videoFile, annFile, logger): #posFile, 
        self.videoFile = videoFile
        self.annFile = annFile
        
        self.segSize = 125
        
        self.noClasses = noClasses
        self.modelPath = modelPath
        
        self.logger = logger
            
        
    def test(self):
        '''
        Loads the model at :data:`modelPath` in a new :class:`EthoCNN.EthoCNN` instace with :data:`noClasses` outputs.
        This will be used to classify all the frames in the video found at :data:`videoFile` location.
        The process is split into steps of maximum :data:`segSize` frames.
        
        The classification is done with a stride of 6, as described in :func:`StackFrames.getTestTensors`. 
        The result is then attributed to the frame in the middle of the interval,
        the 3 frames before, and the 2 frames right after that.
        The current output contains these behaviours: drink, eat, mm+, hang, rear, rest, and walk.
        
        These results are then compared to the ones from the annotation file
        for the corresponding frames to compute the accuracy score and
        fill the confusion matrix.
        
        :return: the accuracy score and the confusion matrix
        :rtype: float, []

        '''
        # print('test interval')
        model = EthoCNN(self.noClasses)
            
        model.load_state_dict(torch.load(self.modelPath))

        if torch.cuda.is_available():
           model.to(torch.device('cuda'))
                
        model.eval()
            
        sumScore = 0
    
        reader = DataReaderAV(self.logger, self.videoFile, self.annFile) 
        if(reader.open() is False):
            print('cannot open video ', self.videoFile)
            return -1
        confusion = np.zeros((self.noClasses, self.noClasses))
        t = 0        
        #model.resetHidden()
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
                crt_y = model(xt)
                npPred = crt_y.data.cpu().numpy()
            
                final_pred = np.argmax(npPred, axis=1)
            
                predex = np.zeros(len(dataSegment))
                bins = int((len(dataSegment)-5)/6)
                
                # print('bins={}, t={}'.format(bins, t))
                
                #map results
                for ia in range(len(final_pred)):
                    final_pred[ia] = mapAnn(final_pred[ia])
                
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
        del model
            
        import gc
        gc.collect()
        torch.cuda.empty_cache()

        # if i % 2 == 0:
        if(t > 0):
            print('tested video: ', self.videoFile, ', avg sumScore = ', sumScore/t)
            return sumScore/t, confusion
        else:
            print('ERROR: something went wrong while processing video: ', self.videoFile)
            return 0, []
            


