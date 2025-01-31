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

#from DataReaderAV import DataReaderAV#, mapAnn
#from StackFrames import getTestTensors
from FrameSelect import FrameSelect


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
        model.load_state_dict(torch.load(self.modelPath, weights_only=True))

        if torch.cuda.is_available():
           model.to(torch.device('cuda'))
                
        model.eval()
        
        #reads the frames from videoFile in segSize blocks.
        # reader = DataReaderAV(logger, self.videoFile)
        # if(reader.open() is False):
        #     print('cannot open video ', self.videoFile)
        #     logger.log('cannot open video {} \n'.format(self.videoFile))
        #     return -1

        t = 0        
        
        logger.log('processing results for video: {}\n'.format(self.videoFile))
        
        #write header
        resultsFile = open(self.outputFile, 'w')
        # resultsFile.write('0:none; 1:drink; 2:eat; 3:groom back; 4:groom; 5:hang; 6:micromovement; 7:rear; 8:rest; 9:walk; v3\n')
        # resultsFile.write('0:drink; 1:eat; 2:mm+; 3:hang; 4:rear; 5:rest; 6:walk; v4\n')
        resultsFile.write('0:drink; 1:eat; 2:groom; 3:hang; 4:mm; 5:rear; 6:rest; 7:walk; v4\n')
        resultsFile.write('frame;annotation;time\n')
        resultsFile.close()

        setSize = 16
        with torch.no_grad():
            fs = FrameSelect(logger, self.videoFile, None, 0)
            if (fs.startReader()):
                while (True):
                    x, y, count, indexList, ptsList = fs.getTestSet(setSize, True)
                    if (count < 1):
                        print('no enough images left in videofile ', self.videoFile)
                        break

                    xt = torch.from_numpy(x).float().cuda()

                

                    # compute predicted annotations by passing the stacked images to the model
                    # logger.log('CNN')
                    crt_y = model(xt)
                    npPred = crt_y.data.cpu().numpy()

                    final_pred = np.argmax(npPred, axis=1)

                    predex = np.zeros(count * 11, dtype=np.int32)
                    bins = count # int((len(dataSegment) -5)/6)

                    # logger.log('unbox')

                    #map results
                    # for ia in range(len(final_pred)):
                    #     final_pred[ia] = mapAnn(final_pred[ia])

                    predex[0] = final_pred[0]
                    predex[1] = final_pred[0]
                    predex[2] = final_pred[0]
                    for i in range(bins):
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
                    predex[-3] = final_pred[-1]
                    predex[-2] = final_pred[-1]
                    predex[-1] = final_pred[-1]

                    # framesA = np.arange(t * self.segSize + 1, (t + 1) * self.segSize + 1, dtype=np.int32)
                    indexes = []
                    ptss = []
                    for j in range(count):
                        for k in range(11):
                            indexes.append(indexList[j][k])
                            ptss.append(ptsList[j][k])
                    padRes = np.stack((indexes, predex, ptss), axis=-1)
                    predFrame = DataFrame(padRes)

                    # logger.log('save results')
                    predFrame.to_csv(self.outputFile, sep=';', header=False, index=False, mode='a')

                    # logger.log('yield {}'.format(perc))
                    # self.model.zero_grad(set_to_none=True)
                    t = t + 1
                    perc = int((t * setSize)/ 490)

                    yield perc
            
            fs.stopReader()
            del fs
        del model
            
        import gc
        gc.collect()
        torch.cuda.empty_cache()

        if(t > 0):
            print('finished processing video: ', self.videoFile)
        else:
            print('ERROR: something went wrong while processing following video: ', self.videoFile)
            


if __name__ == "__main__":
    from Logger import Logger
    import glob
    import sys

    logFile = 'processVideo.log'
    videoDir = ''

    if(len(sys.argv) > 1):
        videoDir = sys.argv[1]
    else:
        print('not enough parameters. please specify the location of the videos')
        exit(1)

    modelPath = '2412_split_90_10_e25.model'

    logPath = videoDir + logFile

    logger = Logger(logPath)
    vCount = 0
    for videoFile in glob.glob(videoDir + '*.mkv'):
        outputFile = videoFile.replace('.mkv', '_v5.csv')
        print('{}. pocessing file: {}'.format(vCount,videoFile))
        vCount += 1
        pc = ProcessVideo(modelPath, 8, videoFile, outputFile)

        crtStep = 0
        try:
            processingIter = pc.process(logger)
            for x in processingIter:
                crtStep += 1
                if(crtStep%200 == 0):
                    mess = 'processing percent: {}'.format(x)
                    logger.log(mess + '\n')
                    print(mess)

        except StopIteration:
            logger.log('finished at step {}'.format(crtStep))
            break

