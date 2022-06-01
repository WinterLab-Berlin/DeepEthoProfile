#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 15:36:14 2021

@author: andrei
"""
from VideoHelper import cutTrainingSegment, cutFinalTrainingSegment, cutOiginalTrainingSegment, cutOiginalTrainingSegment_Crop

from os import path
from random import randint, random

import pandas as pd
import numpy as np

def getAnnData(annFile):
    # print('read  ann file', annFile)
    annDataPD = pd.read_csv(annFile, sep=';', header=1)

    annData = annDataPD["annotation"].to_numpy().tolist()

    #flatten annotation data
    # pv = annData[7]
    # r = 5
    # for i in range(r, len(annData) - r):
    #     cv = annData[i]
    #     if (pv != cv):
    #         newVal = 0
    #         for ii in range(r):
    #             if (cv != annData[i + ii]):
    #                 newVal = newVal + 1

    #         if (newVal <= 2):
    #             pv = cv
    #         else:
    #             annData[i] = pv

    return annData

def getTrainInt(annData, ann, prob, maxCount):
    result = []
    i = -1
    crtData = annData[:]
    offset = 0
    count = 0
    skipFrames=50
    il = 93

    while(len(result) < maxCount):
        # if(count >= maxCount):
        #     break
        
        ld = len(crtData)
        if(ld < 210):
            break
        
        found = False
        for i in range(12, ld - 100):
            
            start = -1
            end = -1
            if(crtData[i] in ann and crtData[i] < ld - 100):
                x = crtData[i:i+10]
                if(x.count(crtData[i]) > 5):
                    start = i-12
                    end = start + il
                    crtData = crtData[end:]
                    
                    if(random() < prob):
                        result.append([start+offset, end+offset])
                        
                    offset+=end
                    found = True
                    # count+=1
                    
                    # #skip some frames
                    # if(len(crtData) > 400):
                    #     crtData = crtData[skipFrames:]
                    #     offset+=skipFrames
                        
                    break
        if(found is False):
            break
    
    return result

def selTrainInt(videoFile, annFile, outFolder, noClasses = 10, minCount=2, save=False):
    annData = getAnnData(annFile)
    ld = len(annData)
    # crtAnnSet = np.zeros(noClasses)
    totalAnn = np.zeros(noClasses)
    selInt = []
    minCount = 2
    # lastInd = 0
    
    selInt = getTrainInt(annData, [1], 0.9, 10)
    
        
    crtSelInt = getTrainInt(annData, [4], 0.2, 3)
    if(len(crtSelInt) > 0):
        for x in crtSelInt:
            selInt.append([x[0], x[1]])

    crtSelInt = getTrainInt(annData, [7], 0.2, 2)
    if(len(crtSelInt) > 0):
        for x in crtSelInt:
            selInt.append([x[0], x[1]])
            # selInt.append([x[0] + lastInd, x[1] + lastInd])
        # lastInd += crtSelInt[-1][1]
            
    crtSelInt = getTrainInt(annData, [9], 0.6, 8)
    if(len(crtSelInt) > 0):
        for x in crtSelInt:
            selInt.append([x[0], x[1]])
            
    crtSelInt = getTrainInt(annData, [5], 0.8, 8)
    if(len(crtSelInt) > 0):
        for x in crtSelInt:
            selInt.append([x[0], x[1]])

    # if(len(selInt) > minCount):
    #     if(len(selInt) > 7): # or lastInd > ld - 400):
    #         break
    
    crtSelInt = getTrainInt(annData, [2], 0.3, 2)
    if(len(crtSelInt) > 0):
        for x in crtSelInt:
            selInt.append([x[0], x[1]])
            
    # crtSelInt = getTrainInt(annData, [6], 0.1, 1)
    # if(len(crtSelInt) > 0):
    #     for x in crtSelInt:
    #         selInt.append([x[0], x[1]])
    #     #     selInt.append([x[0] + lastInd, x[1] + lastInd])
    #     # lastInd += crtSelInt[-1][1]
        
    crtSelInt = getTrainInt(annData, [8], 0.3, 3)
    if(len(crtSelInt) > 0):
        for x in crtSelInt:
            selInt.append([x[0], x[1]])
            
    if(len(selInt) < minCount):
        # if(len(selInt) == 0):
        #     l = int(ld/minCount)
        #     for x in range(minCount):
        #         s = randint(x * l, (x+1) * l - 400)
        #         selInt.append([s, s+130])
        # else:
            s = randint(0, ld - 100)
            selInt.append([s, s+93])

    # print(selInt)
    #compact intervals:
    changed = False
    removed = 0
    while True:
        for x in selInt:
            sx = x[0]
            ex = x[1]
            for y in selInt:
                sy = y[0]
                ey = y[1]
                
                if(sx == sy and ex == ey):
                    continue
                
                if sx < sy:
                    if sy <= ex:
                        if(ex < ey):
                            x[1] = ey
                        removed += 1
                        selInt.remove(y)
                        changed = True
                        break
                            
                else: #'sy > sx'
                    if(sx <= ey):
                        if(ey < ex):
                            y[1] = ex
                        removed += 1
                        selInt.remove(x)
                        changed = True
                        break
            if(changed):
                break
        
        if changed:
            changed = False
        else:
            break
    # print('compacted:', removed)
    # print(selInt)
        
                
    for x in selInt:
        for xx in annData[x[0]:x[1]]:
            totalAnn[xx] += 1
        # print('found interval ', x)
            
        if(save):
            # print('save interval ', x)
            cutFinalTrainingSegment(videoFile, annFile, x[0], x[1]-x[0], outFolder)


    # print('ann for this video: ', totalAnn)
    return totalAnn



    
    
def searchFirst(crtAnnSet, annData, searchSet):
    si = -1
    for x in searchSet:
        if(crtAnnSet[x] > 0):
            csi = annData.index(x)
            if(si < 0 or csi < si):
                si = csi
                
    return si

def getOriginalFiles_PCRS(dataFolder, annFolder):
    #bad tracking files: only on the other set
    videoFiles = [#'01_20180418_1200.mkv', '01_20180418_1800.mkv', '01_20180420_0600.mkv',
                # '02_20180418_1200.mkvi', 
                # '02_20180418_1800.mkv', '02_20180419_0000.mkv',
                # '03_20180418_1200.mkv', '03_20180418_1800.mkv',
                # '03_20180419_0000.mkv', '03_20180419_0600.mkv',
                # '04_20180418_1200.mkv', '04_20180418_1800.mkv', '04_20180419_0000.mkv', '04_20180420_0000.mkv',
                # '05_20180418_1200.mkv', '05_20180418_1800.mkv', '05_20180419_0000.mkv', '05_20180420_0000.mkv',
                # '06_20180418_1200.mkv', '06_20180418_1800.mkv', '06_20180419_0000.mkv',
                # '07_20180418_1200.mkv', '07_20180418_1800.mkv', '07_20180419_0000.mkv', '07_20180419_0600.mkv',
                # '08_20180418_1200.mkv', '08_20180418_1800.mkv', '08_20180419_0000.mkv', '08_20180419_0600.mkv']
                '09_20180418_1200.avi', '09_20180419_0000.avi', '09_20180420_0000.avi',
                '10_20180418_1800.avi', '10_20180419_1200.avi', '10_20180420_0000.avi', '10_20180420_0600.avi']
    #bad tracking files: 
    annFiles = [#'01_20180418_1200_RS.csv',  '01_20180418_1800_RS.csv', '01_20180420_0600_PC.csv',
                # '02_20180418_1200_RS.csv', 
                # '02_20180418_1800_RS.csv', '02_20180419_0000_RS.csv',
                # '03_20180418_1200_RS.csv', '03_20180418_1800_RS.csv',
                # '03_20180419_0000_RS.csv', '03_20180419_0600_RS.csv',
                # '04_20180418_1200_PC.csv', '04_20180418_1800_PC.csv', '04_20180419_0000_PC.csv', '04_20180420_0000_PC.csv',
                # '05_20180418_1200_RS.csv', '05_20180418_1800_RS.csv', '05_20180419_0000_RS.csv', '05_20180420_0000_RS.csv',
                # '06_20180418_1200_RS.csv', '06_20180418_1800_RS.csv', '06_20180419_0000_PC.csv',
                # '07_20180418_1200_PC.csv', '07_20180418_1800_PC.csv', '07_20180419_0000_PC.csv', '07_20180419_0600_PC.csv',
                # '08_20180418_1200_RS.csv', '08_20180418_1800_RS.csv', '08_20180419_0000_RS.csv', '08_20180419_0600_RS.csv']
                '09_20180418_1200_PC.csv', '09_20180419_0000_RS.csv', '09_20180420_0000_RS.csv',
                '10_20180418_1800_PC.csv', '10_20180419_1200_PC.csv', '10_20180420_0000_PC.csv', '10_20180420_0600_RS.csv']
    
    result = []
    
    for i in range(len(videoFiles)):
        crtVideoFile = videoFiles[i]
        # crtPosFile = crtVideoFile.replace('.avi', '.csv')
        crtAnnFile = annFiles[i]
        
        annFile = path.join(annFolder, crtAnnFile)
        videoFile = path.join(dataFolder, crtVideoFile)
        # posFile = path.join(dataFolder, crtPosFile)
        
        result.append([videoFile, annFile]) #posFile, 
        
    return result

def getTrainigFiles_PCRS(dataFolder, annFolder):
    #bad tracking files: only on the other set
    videoFiles = ['01_20180418_1200.avi', '01_20180418_1800.avi', '01_20180420_0600.avi',
                # '02_20180418_1200.avi', 
                '02_20180418_1800.avi', '02_20180419_0000.avi',
                '03_20180418_1200.avi', '03_20180418_1800.avi',
                '03_20180419_0000.avi', '03_20180419_0600.avi',
                '04_20180418_1200.avi', '04_20180418_1800.avi', '04_20180419_0000.avi', '04_20180420_0000.avi',
                '05_20180418_1200.avi', '05_20180418_1800.avi', '05_20180419_0000.avi', '05_20180420_0000.avi',
                '06_20180418_1200.avi', '06_20180418_1800.avi', '06_20180419_0000.avi',
                '07_20180418_1200.avi', '07_20180418_1800.avi', '07_20180419_0000.avi', '07_20180419_0600.avi',
                '08_20180418_1200.avi', '08_20180418_1800.avi', '08_20180419_0000.avi', '08_20180419_0600.avi']
                # '09_20180418_1200.avi', '09_20180419_0000.avi', '09_20180420_0000.avi']#,
                # '10_20180418_1800.avi', '10_20180419_1200.avi', '10_20180420_0000.avi', '10_20180420_0600.avi']
    #bad tracking files: 
    annFiles = ['01_20180418_1200_RS.csv',  '01_20180418_1800_RS.csv', '01_20180420_0600_PC.csv',
                # '02_20180418_1200_RS.csv', 
                '02_20180418_1800_RS.csv', '02_20180419_0000_RS.csv',
                '03_20180418_1200_RS.csv', '03_20180418_1800_RS.csv',
                '03_20180419_0000_RS.csv', '03_20180419_0600_RS.csv',
                '04_20180418_1200_PC.csv', '04_20180418_1800_PC.csv', '04_20180419_0000_PC.csv', '04_20180420_0000_PC.csv',
                '05_20180418_1200_RS.csv', '05_20180418_1800_RS.csv', '05_20180419_0000_RS.csv', '05_20180420_0000_RS.csv',
                '06_20180418_1200_RS.csv', '06_20180418_1800_RS.csv', '06_20180419_0000_PC.csv',
                '07_20180418_1200_PC.csv', '07_20180418_1800_PC.csv', '07_20180419_0000_PC.csv', '07_20180419_0600_PC.csv',
                '08_20180418_1200_RS.csv', '08_20180418_1800_RS.csv', '08_20180419_0000_RS.csv', '08_20180419_0600_RS.csv']
                # '09_20180418_1200_PC.csv', '09_20180419_0000_RS.csv', '09_20180420_0000_RS.csv']#,
                # # '10_20180418_1800_PC.csv', '10_20180419_1200_PC.csv', '10_20180420_0000_PC.csv', '10_20180420_0600_RS.csv']
    
    result = []
    
    for i in range(len(videoFiles)):
        crtVideoFile = videoFiles[i]
        crtAnnFile = annFiles[i]
        
        annFile = path.join(annFolder, crtAnnFile)
        videoFile = path.join(dataFolder, crtVideoFile)
        
        result.append([videoFile, annFile]) #posFile, 
        
    return result



if __name__ == "__main__":
        
    outFolder = '/home/andrei/Videos/2205_trainCropVideos_21'
    dataFolder = '/home/andrei/Videos/2205_cropVideos' #train_orig'
    annFolder = '/home/andrei/Videos/2205_cropVideos/ann_train'
    
    intervals_PCRS = [[0, 7500], [45000, 52500], [90000, 97500], [135000, 142500], [180000, 187500], [225000, 232500],
                      [270000, 277500], [315000, 322500], [360000, 367500], [405000, 412500], [450000, 457500], [495000, 502500]]
    # intervals_RS = [[1, 7500], [270000, 277500]]
    noClasses = 10
    inputFiles = getTrainigFiles_PCRS(dataFolder, annFolder)    
    totalAnn = np.zeros(noClasses)

    for x in inputFiles:
        # print('select ann intervals for ', x)
        for crtInt in intervals_PCRS:
            segVideo, segAnn = cutOiginalTrainingSegment_Crop(x[0], x[1], crtInt[0], crtInt[1] - crtInt[0])
            # print('proc video ', segVideo)
            totalAnn += selTrainInt(segVideo, segAnn, outFolder, minCount=2, save=True)
            # with np.printoptions(suppress=True):
            #     print('END ann: ', totalAnn)
            # break
        # break
    with np.printoptions(suppress=True):
        print('END ann: ', totalAnn)


#01.12.21 selected train intervals from recordings 3-8, 1 extra round for ann [4,8] and another for [8]
# = step 1020, cost=0.023405371455900974, current annTotalSet = [    3 20408 36510     0 60728 35906 65923 43335 53307 37480]
 #= = = for this full step, annTotalSet =  [    3 20979 36555     0 60841 35906 66801 43695 53318 37742]
#FULL STEP! avg cost is:  0.02335223696143523
