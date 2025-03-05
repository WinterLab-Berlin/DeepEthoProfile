#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
the TestInterval class

@author: Andrei Istudor     andrei.istudor@gmail.com
"""
import numpy as np
from EthoCNN import EthoCNN#, getTensors
import torch
from sklearn.metrics import accuracy_score

# from DataReader import DataReader
from DataReaderAV import DataReaderAV#, mapAnn2
# from StackFrames import  getTestTensors
from Logger import Logger
from FrameSelect import FrameSelect


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
            
        model.load_state_dict(torch.load(self.modelPath, weights_only=True))

        if torch.cuda.is_available():
           model.to(torch.device('cuda'))
                
        model.eval()
            
        sumScore = 0
    
        # reader = DataReaderAV(self.logger, self.videoFile, self.annFile)
        # if(reader.open() is False):
        #     print('TI - cannot open video: ', self.videoFile)
        #     return -1
        confusion = np.zeros((self.noClasses, self.noClasses))
        t = 0        
        # step = 5
        # print('opened ann ', self.annFile)
        #model.resetHidden()
        setSize = 16
        with torch.no_grad():
            fs = FrameSelect(self.logger, self.videoFile, self.annFile, 0)
            if(fs.startReader()):
                while(True):
                    x, y, count = fs.getTestSet(setSize)
                    if(count < 1):
                        print('no enough images left in videofile ', self.videoFile)
                        break
                    
                    xt = torch.from_numpy(x).float().cuda()
                    # bins = len(xt)
                    # print(bins)
                    # print(y.shape)
                    # print('y:', y)
                    # if(bins < 1):
                    
                    # print('frames={}, bins={}, t={}'.format(len(x), bins, t))
                    
                # Forward pass: Compute predicted y by passing x to the model
                    crt_y = model(xt)
                    npPred = crt_y.data.cpu().numpy()
                
                    final_pred = np.argmax(npPred, axis=1)

                    predex = np.zeros(count*11, dtype=int)
                    yex = y[:count].flatten()

                    for i in range(count):
                        ii = i * 11 + 5

                        predex[ii-5] = final_pred[i]
                        predex[ii-4] = final_pred[i]
                        predex[ii-3] = final_pred[i]
                        predex[ii-2] = final_pred[i]
                        predex[ii-1] = final_pred[i]
                        predex[ii] = final_pred[i]
                        predex[ii+1] = final_pred[i]
                        predex[ii+2] = final_pred[i]
                        predex[ii+3] = final_pred[i]
                        predex[ii+4] = final_pred[i]
                        predex[ii+5] = final_pred[i]

                    score = accuracy_score(yex, predex)
                    for i in range(len(yex)):
                        confusion[yex[i], int(predex[i])] += 1
                
                    sumScore = sumScore + score
                
                    t = t + 1

                    if(count < setSize):
                        # print('finished video')
                        break
                
            fs.stopReader()
            del fs
        del model
            
        import gc
        gc.collect()
        torch.cuda.empty_cache()

        if(t > 0):
            # print('tested video: ', self.videoFile, ', avg sumScore = ', sumScore/t)
            return sumScore/t, confusion
        else:
            # print('ERROR: something went wrong while processing video: ', self.videoFile)
            return -1, []
            


