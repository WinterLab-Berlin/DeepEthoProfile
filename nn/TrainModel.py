#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The TrainModel class 


@author: Andrei Istudor     andrei.istudor@gmail.com
"""
import gc
import tracemalloc

import torch
import torch.nn
import torch.optim
from torch.autograd import Variable
from random import randint

import numpy as np
from os import path
# from pathlib import Path
import glob
from random import shuffle, random
from sklearn.metrics import accuracy_score


from EthoCNN import EthoCNN
from TrainInterval import TrainInterval
from Logger import Logger
from TestModel import TestModel

noClasses = 8

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
    
    def __init__(self, noClasses, log, modelPath = None):
        print('init TrainModel')
        #TODO: init model 
        self.model = None
        self.trainIntervals = []
        
        self.running = False
        self.loadedEpoch = 0
        
        self.noClasses = noClasses
        self.initModel(modelPath)
        
        self.stagnating = 0
        
        self.logger = log
        
    def initModel(self, modelPath = None):
        '''
        Initializes the :data:`model`, the :data:`optimizer` and the :data:`criterion`.
        
        If cuda is available, they will all be transfered to the GPU memory.

        '''
        
        self.model = EthoCNN(self.noClasses)
        
        if(modelPath is None):
           # the weights apparently apply only for the batch, which is not useful for the current training data
            # cWeight = torch.tensor  ([2.55, 1.14, 0.72, 1.25, 0.69, 0.89, 0.78, 1.5]).cuda()
            #self.model.train()       
            # optimizer = torch.optim.Adam(model.parameters(), lr=0.07)
            self.criterion = torch.nn.CrossEntropyLoss() # weight=cWeight)

            if torch.cuda.is_available():
                print('cuda')
                self.model = self.model.cuda()
                self.criterion = self.criterion.cuda()
                
            self.optimizer = torch.optim.SGD(self.model.parameters(), lr = 0.03)#, momentum=0.5)#, weight_decay = 0.0001) #, momentum=0.9
            self.scheduler = torch.optim.lr_scheduler.ExponentialLR(self.optimizer, gamma=0.99)
        else:
            print('load full model')
            checkpoint = torch.load(modelPath, weights_only=False)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.criterion = checkpoint['loss']
            
            if torch.cuda.is_available():
                print('cuda')
                self.model = self.model.cuda()
                self.criterion = self.criterion.cuda()
                
            self.optimizer = torch.optim.SGD(self.model.parameters(), lr = 0.03, momentum=0.5)
            self.scheduler = torch.optim.lr_scheduler.ExponentialLR(self.optimizer, gamma=0.99)
            
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.loadedEpoch = checkpoint['epoch'] + 1
            # self.scheduler = checkpoint['scheduler']
            # print('loadedEpoch = ', self.loadedEpoch)
        #     self.scheduler = torch.optim.lr_scheduler.ExponentialLR(self.optimizer, gamma=0.99)
        # else:
        #     self.scheduler = torch.optim.lr_scheduler.ExponentialLR(self.optimizer, gamma=0.98)
        
        self.model.train()       
        

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
        
        
    def trainSet(self, imS, annS, count):
        # xf = np.zeros(8)
        # for xi in annS:
        #     xf[xi] += 1
        # # if(min(xf) < 1):
        # print('train set: ', xf)

        xt = torch.from_numpy(imS[:count]).float().cuda()
        yt = torch.from_numpy(annS[:count]).long().cuda()
        # print(annS)
        score = 0
        confusion = np.zeros((self.noClasses, self.noClasses))
        

        self.optimizer.zero_grad()

        # compute predicted annotations by passing the stacked images to the model
        crt_y = self.model(xt) #, posT
        
        # Compute loss
        loss = self.criterion(crt_y, yt)
    
        loss.backward()
        self.optimizer.step()
        
        if(np.isnan(loss.item())):
            print(' ! ! ! ! loss is NaN')
        else:
#debug/status data:
            npPred = crt_y.data.cpu().numpy()
            final_pred = np.argmax(npPred, axis=1)
            ann = yt.data.cpu().numpy()
            score = accuracy_score(ann, final_pred)
            for i in range(len(ann)):
                confusion[ann[i], final_pred[i]] += 1

        return loss.item(), score, confusion

    def trainBuf(self, imBuff, setSize, stackSize):
        loadMore = False
        storedBuf = 0
        for cb in range(self.noClasses - 1):
            b = imBuff[cb+1]
            s = len(b)
            if (s == 0):
                loadMore = True
                break
            else:
                storedBuf += s

        if (loadMore is True):
            # print('load more')
            return False, 0, None, None, None, None

        if (storedBuf < setSize):
            # print('not enough images')
            return False, 0, None, None, None, None

        # Start to trace memory
        tracemalloc.start()

        outi = np.array(np.zeros((setSize, stackSize, 256, 256), dtype=np.float16))
        outa = np.array(np.zeros(setSize, dtype=int))
        # print('stored buffer = ', storedBuf)
        selInt = []
        for cb in range(self.noClasses):
            shuffle(imBuff[cb])
        selInt.append(imBuff[0].pop(0))
        startA = 6 #randint(0, 7)
        maxL = 0
        for cb in range(self.noClasses - 1):
            if(len(imBuff[cb + 1]) > maxL):
                maxL = len(imBuff[cb + 1])
                startA = cb

        while (len(selInt) < setSize):
            for cb in range(self.noClasses - 1):
                crti = cb + startA
                crti %= (self.noClasses - 1)
                if (len(imBuff[crti + 1]) > 0):
                    selInt.append(imBuff[crti + 1].pop(0))

                if (len(selInt) == setSize):
                    break

        shuffle(selInt)

        for ci in range(len(selInt)):
            crtIm, crtAnn = selInt[ci]
            outi[ci] = crtIm
            outa[ci] = crtAnn

        # print('train set')
        crtLoss, crtScore, crtConfusion = self.trainSet(outi, outa, len(selInt))
        if (np.isnan(crtLoss)):
            print('loss is NaN')
            # self.scheduler.step()
            return False, 0, None, None, None, None
        else:
            annSet = np.zeros(self.noClasses)
            for a in outa:
                annSet[a] += 1

            # selInt.clear()
            del outi
            del outa
            # del selInt
            gc.collect()
            # Clear traces of memory blocks allocated by Python
            # before moving to the next section.
            tracemalloc.clear_traces()

            return True, len(selInt), crtLoss, crtScore, crtConfusion, annSet

    def trainNewEpoch(self, epoch, drinkBuffer):
        confusion = np.zeros((self.noClasses, self.noClasses))
        annTotalSet = np.zeros(self.noClasses)
        status = []
        started = []
        stackSize = 11
        setSize = 16
        
        for i in self.trainIntervals:
            # i.startNew(self.logger)
            status.append(True)
            started.append(False)
        
        score = 0
        loss = 0
        confusion = np.zeros((self.noClasses, self.noClasses))
        annSet = np.zeros(self.noClasses)
        
        i = 0
        totalFrames = 0
        totalTrains = 0

        imBuff = []
        for i in range(self.noClasses):
            imBuff.append([])

        previousDrink = len(drinkBuffer)
        if(previousDrink > 0):
            print('recover drink ', previousDrink)
            for d in drinkBuffer:
                imBuff[0].append(d)

        stopping = False
        hasDrink = 0

        localIntervals = min(100, len(self.trainIntervals))
        # crtFinished = status.count(False)
        
        while(status.count(True) > 4):
            if(stopping):
                print('stopping')
                break
            
            for tii in range(localIntervals):
                if(not started[tii]):
                    self.trainIntervals[tii].startNew(self.logger)
                    started[tii] = True

                if(status[tii]):
                    ti = self.trainIntervals[tii]
                    imS, ann, finished = ti.getNextStackedImage(self.logger)
                    if(finished):
                        status[tii] = False
                        # if(crtFinished < status.count(False)):
                        if(localIntervals < len(self.trainIntervals)):
                            # print('add interval after ', totalFrames, ', now = ', localIntervals, ', and finished = ', status.count(False))
                            localIntervals += 1
                        # else:
                        #     if(status.count(True) < 20):
                        #         stopping = True
                        #         break
                        # else:
                        #     print('finished adding intervals {}, finished = {}'.format(localIntervals, status.count(False)))
                    else:
                        skipMore = 0.6

                        if(ann in [6, 1] and random() < 0.22):
                            continue
                        if(status.count(True) < setSize):
                            skipMore = 0.2
                        if(ann in [6, 1 , 2, 4] and random() < skipMore):
                            continue

                        # if(ann != 0):
                        #     tl = 0
                        #     iz = 0
                        #     for xx in range(len(imBuff) - 1):
                        #         iz = len(imBuff[xx+1])
                        #         if(iz == 0 and ann == xx+1):
                        #             # print('found one missing ', ann)
                        #             tl = 0
                        #             break
                        #         tl += iz
                        #
                        #     if(tl > 3000):
                        #         print('memory almost full ', tl)
                        #         continue

                        imBuff[ann].append((imS, ann))

                        tResult = True
                        while(tResult and len(imBuff[0]) > 0):
                            tResult, crtFrames, crtLoss, crtScore, crtConfusion, crtAnnSet = self.trainBuf(imBuff, setSize, stackSize)
                            if(tResult is True):
                                totalFrames += crtFrames
                                totalTrains += 1
                                loss += crtLoss
                                score += crtScore
                                confusion += crtConfusion
                                annSet += crtAnnSet

                                gc.collect()

                                if (totalTrains % 50 == 0):
                                    print(' = after {} images - - - score = {:.2%}, loss = {:.4}, annTotalSet = {}'.format(
                                        totalFrames, score / totalTrains, loss / totalTrains, np.uint32(annSet)))
                                    # tl = []
                                    # for xx in range(len(imBuff)):
                                    #     tl.append(len(imBuff[xx]))
                                    # print('current stored set: {} with total = {}'.format(tl, sum(tl)))

                                # tpC = 0
                                # taC = 0
                                # for i in range(len(confusion)):
                                #     for j in range(len(confusion[i])):
                                #         taC += confusion[i, j]
                                #         if(i == j):
                                #             tpC += confusion[i, j]
                                # print(' = = = train acc so far (with dropout) = {}'.format(tpC / taC))
                                # with np.printoptions(suppress=True):
                                #     print('confusion: \n', confusion

                else:
                    # print('status {} is {}'.format(tii, status[tii]))
                    pass

        if (len(imBuff[0]) > 0):
            tResult = True
            while (tResult):
                tResult, crtFrames, crtLoss, crtScore, crtConfusion, crtAnnSet = self.trainBuf(imBuff, setSize, stackSize)
                if (tResult is True):
                    totalFrames += crtFrames
                    totalTrains += 1
                    loss += crtLoss
                    score += crtScore
                    confusion += crtConfusion
                    annSet += crtAnnSet

        tl = []
        for xx in range(len(imBuff)):
            tl.append(len(imBuff[xx]))
        print('current stored set: {} with total = {}'.format(tl, sum(tl)))

        drinkBuffer.clear()
        for d in imBuff[0]:
            drinkBuffer.append(d)

        for i in imBuff:
            i.clear()
        imBuff.clear()
        del imBuff

        print(' = after {} images - - - score = {:.2%}, loss = {:.4}, annTotalSet = {}'.format(
            totalFrames, score/totalTrains, loss/totalTrains, np.uint32(annSet)))
        tpC = 0
        taC = 0
        for i in range(len(confusion)):
            for j in range(len(confusion[i])):
                taC += confusion[i, j]
                if(i == j):
                    tpC += confusion[i, j]
        print(' = = = train acc so far (with dropout) = {:.2%}'.format(tpC / taC))
        with np.printoptions(suppress=True):
            print('confusion: \n', confusion)


        if(totalTrains > 0):
            return loss/totalTrains
        else:
            return -1
            
            
                
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
        i = 0
        
        # shuffle(self.trainIntervals)
        drinkBuffer = []

        for i in range(epochs):
            print('train step ', i + self.loadedEpoch, ', with ', len(self.trainIntervals), ' intervals')
            if(self.running):
                shuffle(self.trainIntervals)
                avgCost = self.trainNewEpoch(i, drinkBuffer)


                print('FULL STEP! avg cost is: ', avgCost)
                
                if(i + self.loadedEpoch > 0):
                    self.saveModel('step_{}.model'.format(i + self.loadedEpoch))
                # self.saveCheckpoint(i, 'check_{}.model'.format(i + self.loadedEpoch))
                    
            # if(i > 5):
            self.scheduler.step()
            print(' run scheduler at the end of an EPOCH, last computed lr = {}'.format(self.scheduler.get_last_lr()))
            
        self.saveCheckpoint(i + self.loadedEpoch, 'check_{}.model'.format(i + self.loadedEpoch))

    # #TODO: this should be called async
    # def stop(self):
    #     self.running = False
    def saveCheckpoint(self, epoch, path):
        print('save checkpoint for epoch {} at {} '.format(epoch, path))
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': self.criterion,
            # 'scheduler': self.scheduler,
            }, path)
        
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
        
    def countAnn(self):
        import pandas as pd
        
        result = np.zeros(self.noClasses)
        
        for i in self.trainIntervals:
            annFile = i.annFile
            annData = pd.read_csv(annFile, sep=';', header=1)
            for x in annData['annotation']:
                result[x] += 1
                
        print('complete annotation data: ', result)
                
        

if __name__ == "__main__":
    import sys
    
    print('train command: ', sys.argv)
    trainVideoPath = ''
    testVideoPrefix = ''

    if (len(sys.argv) > 1):
        # global trainVideoPath
        print('training folder: ', sys.argv[1])
        trainVideoPath = sys.argv[1]
    else:
        print ('not enough parameters')
        exit(1)
    
    if (len(sys.argv) > 2):
        # global trainVideoPath
        print('test video prefix: ', sys.argv[2])
        testVideoPrefix = sys.argv[2]
    else:
        print ('no video prefix given')
        exit(1)

    log = Logger('train.log')

    modelPath = None
    if (len(sys.argv) > 3):
        modelPath = sys.argv[3]
    # modelPath = './mouse.modular.model'
    
    epochs = 40
    loadedEpoch = 0
    
    #train
    trainModel = TrainModel(noClasses, log, modelPath)
    loadedEpoch = trainModel.loadedEpoch
    testVideos = []

    #for annFile in glob.glob(trainVideoPath + '*_map_new.csv'):
    #    videoFile = annFile.replace('_map_new.csv', '.avi')
    #    trainModel.addTrainInterval(videoFile, annFile)

    for videoFile in glob.glob(trainVideoPath + '*.avi'):
        annFile = videoFile.replace('.avi', '_map.csv')
        newAnnFile = videoFile.replace('.avi', '_map_new.csv')
        crtAnnFile = annFile
        if (path.exists(newAnnFile)):
            crtAnnFile = newAnnFile
        elif(path.exists(annFile)):
            crtAnnFile = annFile
        else:
            print('missing data for file ', videoFile)
            continue

        if(crtAnnFile.find(testVideoPrefix) > 0):
            testVideos.append((videoFile, crtAnnFile))
        else:
            newAnnFile2 = videoFile.replace('.avi', '_map_new_v2.csv')
            if(path.exists(newAnnFile2)):
                crtAnnFile = newAnnFile2

            trainModel.addTrainInterval(videoFile, crtAnnFile)

        # newAnnFile = videoFile.replace('.avi', '_map_new.csv')
        # newAnnFile2 = videoFile.replace('.avi', '_map_new_v2.csv')
        #
        # if(path.exists(newAnnFile2)):
        #     trainModel.addTrainInterval(videoFile, newAnnFile2)
        # elif(path.exists(newAnnFile)):
        #     trainModel.addTrainInterval(videoFile, newAnnFile)
        # if(path.exists(annFile)):
        #     trainModel.addTrainInterval(videoFile, annFile)
        # else:
        #     print('missing data for file ', videoFile)


    # # # trainModel.countAnn()

    # # # trainModel.train(epochs)
    trainModel.train(epochs)
    # # #trainModel.saveModel(modelPath)
    trainModel.cleanup()
    del trainModel


    #test    
    dataFolder = ''
    
    if(len(sys.argv) > 2):
        dataFolder = sys.argv[2]
        print('test videos folder: ', sys.argv[2])
        # if(len(sys.argv) > 3):
        for x in range(max(2, loadedEpoch), epochs + loadedEpoch):#epochs-10):
            # modelName = 'mouse_v2.model' 
            modelName = 'step_{}.model'.format(x)#epochs - x)
            print(' - - - testing model: {} - - - '.format( modelName))
            testModel = TestModel(noClasses, modelName, log)

            for (crtVideo, crtAnn) in testVideos:
                testModel.addTestInterval(crtVideo, crtAnn)

            # for crtVideo in glob.glob(dataFolder + '*.avi'):
            #     crtAnn = crtVideo.replace('.avi', '_map.csv')
            #     newAnn = crtVideo.replace('.avi', '_map_new.csv')
            #     newAnnFile2 = crtVideo.replace('.avi', '_map_new_v2.csv')
            #
            #     # if(path.exists(newAnnFile2)):
            #     #     #testModel.addTrainInterval(crtVideo, newAnnFile2)
            #     #     print('not testting with v2 annotations ', newAnnFile2)
            #     #     #continue
            #     # if(path.exists(newAnn)):
            #     #     testModel.addTestInterval(crtVideo, newAnn)
            #     if(path.exists(crtAnn)):
            #         testModel.addTestInterval(crtVideo, crtAnn)
            #     else:
            #         print('missing data for file ', crtVideo)
                
            print('added test files')
            testModel.test()
            del testModel
    else:
        print('no testing data')
        
    
        
