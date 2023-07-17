#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
the ProcessVideo class

@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""

import numpy as np
from EthoCNN import EthoCNN
import torch
from pandas import DataFrame

from DataReaderAV import DataReaderAV, mapAnn
from StackFrames import getTestTensors

class ProcessVideo():
    '''
    Wrapper for the instiating the CNN with a specified model and using it to process a video file. 
    
    
    '''

    #: the full path to the video that will be processed by the current instance
    videoFile: str
    
    #: the full path to the output file where the results will be stored
    outputFile: str
    
    #: full path to trained model that will be used
    modelPath: str
    
    #: number of classed used by the model (current model uses 10)
    noClasses: str
    
    #: maximum number of frames that will be read and processed at a time - depends on the available memory
    segSize: int

    def __init__(self, modelPath, noClasses, videoFile, outputFile, segSize=125): 
        self.videoFile = videoFile
        self.outputFile = outputFile
        self.noClasses = noClasses
        self.modelPath = modelPath
        self.segSize = segSize
        
    def process(self, logger):
        '''
        Generator function for behaviour classification.
        
        Creates a :class:`EthoCNN.EthoCNN` instance with :data:`noClasses` outputs 
        and loads the trained model present in :data:`modelPath`. The resulting 
        object will be running in evaluation mode, and, if available, on the CUDA environment.
        
        For each call, the method will process a maximum of :data:`segSize` frames,
        store the results in the output file and return the percentage to the
        total frames that have been processed so far.
        
        Each classification is done for a set of 11 frames. The process is 
        performed with a stride of 5 as described in :class:`StackFrames.getTestTensors`. 
        The result is then attributed to the frame in the middle of the interval,
        the 3 frames before, and the 2 frames right after that. 
        Therefore there are no behaviour bouts  shorter than 240ms. 
        This is conform to the behaviour definition and 
        avoides noisy results, while speeding up the processing.
        
        The current output contains these behaviours: drink, eat, mm+, hang, rear, rest, and walk
        
        :param logger: simple logger used mostly for debugging
        :type logger: Logger.Logger
        :yield: the percentage of frames already processed
        :rtype: int

        '''
        # print('process video')
        model = EthoCNN(self.noClasses)
        model.load_state_dict(torch.load(self.modelPath))

        if torch.cuda.is_available():
           model.to(torch.device('cuda'))
                
        model.eval()
        
        #reads the frames from videoFile in segSize blocks.
        reader = DataReaderAV(logger, self.videoFile)
        if(reader.open() is False):
            print('cannot open video ', self.videoFile)
            logger.log('cannot open video {} \n'.format(self.videoFile))
            return -1

        t = 0        
        
        logger.log('processing results for video: {}\n'.format(self.videoFile))
        
        #write header
        resultsFile = open(self.outputFile, 'w')
        # resultsFile.write('0:none; 1:drink; 2:eat; 3:groom back; 4:groom; 5:hang; 6:micromovement; 7:rear; 8:rest; 9:walk; v3\n')
        resultsFile.write('0:drink; 1:eat; 2:mm+; 3:hang; 4:rear; 5:rest; 6:walk; v4\n')
        resultsFile.write('frame;annotation;time\n')
        resultsFile.close()
        

        with torch.no_grad():
            for dataSegment in reader.readFrames(self.segSize):
                if(len(dataSegment) < 16):
                    logger.log('read too few frames: {}'.format(len(dataSegment)))
                    break
                
                data = np.array(dataSegment, dtype=object)
                x = data[:, 2]
                frameIdx = data[:, 0]
                framePts = data[:, 1]

                # logger.log('get Tensors')
                xt = getTestTensors(x)

                # compute predicted annotations by passing the stacked images to the model
                # logger.log('CNN')
                crt_y = model(xt)
                npPred = crt_y.data.cpu().numpy()
            
                final_pred = np.argmax(npPred, axis=1)
            
                predex = np.zeros(len(dataSegment) , dtype=np.int32)
                bins = int((len(dataSegment) -5)/6)
                
                # logger.log('unbox')

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

                # framesA = np.arange(t * self.segSize + 1, (t + 1) * self.segSize + 1, dtype=np.int32)
                padRes = np.stack((frameIdx, predex, framePts), axis=-1)
                predFrame = DataFrame(padRes)

                # logger.log('save results')
                predFrame.to_csv(self.outputFile, sep=';', header=False, index=False, mode='a')

                perc = int((t * self.segSize * 100 + 1)/ reader.totalFrames)
                # logger.log('yield {}'.format(perc))
                # self.model.zero_grad(set_to_none=True)
                t = t + 1

                yield perc
            
        reader.close()
        del reader
        del model
            
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

