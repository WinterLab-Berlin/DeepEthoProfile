#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 15:36:14 2021

@author: andrei
"""
from VideoHelper import cutTrainingSegment, cutFinalTrainingSegment, cutOiginalTrainingSegment

from os import path
from random import randint, random

import pandas as pd
import numpy as np

def getAnnData(annFile):
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

def getTrainInt(annData, ann, length, prob, maxCount):
    result = []
    i = -1
    crtData = annData[:]
    offset = 0

    while(len(result) < maxCount):
        ld = len(crtData)
        if(ld < 400):
            break
        
        found = False
        for i in range(12, ld - 201):
            
            start = -1
            end = -1
            if(crtData[i] in ann and crtData[i] < ld - 200):
                start = i-12
                count = 1
                if(random.random() < prob):
                    found = True
                    if(length > 1 and crtData[i] < ld - (200 * length) ):
                        for xx in range(length - 1):
                            if(random.random() < prob ):
                                break
                            si = i + (xx+1) * 200
                            ni = crtData[si:si+200]
                            for cx in ni:
                                if(ni in ann):
                                    count += 1
                                    break
                end = start + count * 200
                crtData = crtData[end:]
                
                if(found):
                    result.append([start+offset, end+offset])
                    
                offset+=end
                break
        if(not found):
            break
        
    
    return result

def selTrainInt(videoFile, annFile, outFolder, noClasses = 10, minCount=2, save=False):
    annData = getAnnData(annFile)
    ld = len(annData)
    # crtAnnSet = np.zeros(noClasses)
    totalAnn = np.zeros(noClasses)
    selInt = []
    lastInd = 0
    
    selInt = getTrainInt(annData, [1, 5, 9], 2, 0.8, 8)
    
    while True:
        if(len(selInt) > 0):
            lastInd = selInt[-1][1]
        
        if(len(selInt) > minCount):
            if(len(selInt) > 6 or lastInd > ld - 400):
                break
            
        crtSelInt = getTrainInt(annData[lastInd:], [7], 1, 0.5, 2)
        if(len(crtSelInt) > 0):
            for x in crtSelInt:
                selInt.append([x[0] + lastInd, x[1] + lastInd])
            lastInd += crtSelInt[-1][1]
        
    
        if(len(selInt) > minCount):
            if(len(selInt) > 7 or lastInd > ld - 400):
                break
        
        crtSelInt = getTrainInt(annData[lastInd:], [2, 4, 8], 1, 0.5, 2)
        if(len(crtSelInt) > 0):
            for x in crtSelInt:
                selInt.append([x[0] + lastInd, x[1] + lastInd])
            lastInd += crtSelInt[-1][1]
            
        if(len(selInt) < minCount):
            if(len(selInt) == 0):
                l = int(ld/minCount)
                for x in range(minCount):
                    s = random.randint(x * l, (x+1) * l - 200)
                    selInt.append([s, s+200])
            elif(lastInd < ld - 400):
                s = random.randint(lastInd, ld - 200)
                selInt.append([s, s+200])
            else:
                e = selInt[0][0]
                if(e > 200):
                    s = random.randint(0, e - 200)
                    selInt.append([s, s+200])
                else:
                    print('strange to be here...')
                    
        if(selInt[0][0] > ld / 2):
            e = selInt[0][0]
            if(e > 200):
                s = random.randint(0, e - 200)
                selInt.append([s, s+200])
            
        break
                
    for x in selInt:
        for xx in annData[x[0]:x[1]]:
            totalAnn[xx] += 1
        # print('found interval ', x)
            
        if(save):
            print('save interval ', x)
            cutFinalTrainingSegment(videoFile, annFile, x[0], x[1]-x[0], outFolder)


    # print('ann for this video: ', totalAnn)
    return totalAnn


def selectTrainIntervals(videoFile, posFile, annFile, outFolder, noClasses, totalAnn, save=True):
    # print('select intervals for file ', videoFile)
    annData = getAnnData(annFile)
    ld = len(annData)
    crtAnnSet = np.zeros(noClasses)
    minSeg = 140
    maxAnn = 25000

    #check minimum interval > 64
    if(ld < minSeg):
        print('ann data segment is too short')
        return crtAnnSet

    for x in annData:
        crtAnnSet[x] = crtAnnSet[x] + 1

    sc = [1, 9]
    #looking for 1:drink 5:hang 7:rear 9:walk
    
    si = -1
    ei = 0
    finalResult = np.zeros(noClasses)
    
    pMax = np.argmax(crtAnnSet)
    
    if(totalAnn[2] < np.mean(totalAnn)):
        sc.append(2)
    elif(totalAnn[2] < maxAnn):
        if(randint(0,4) == 2):
            sc.append(2)
            
    if(totalAnn[4] < np.mean(totalAnn)):
        sc.append(4)
    elif(randint(0,4) == 2):
        sc.append(4)
            
    if(totalAnn[7] < np.mean(totalAnn)):
        sc.append(7)
        
    if(totalAnn[5] < np.mean(totalAnn)):
        sc.append(5)
    
    si = searchFirst(crtAnnSet, annData, sc)

    if(totalAnn[8] < np.mean(totalAnn)):
        sc.append(8)
    elif(totalAnn[8] < maxAnn):
        if(randint(0,4) == 2):
            sc.append(8)
    
    if(si >= 0):
        if(si > 4):
            si = si - 4
        else:
            si = 0
            
        while(True):
            result = np.zeros(noClasses)
            # print('select interval with searched behaviors')
            if(ld - si > 64):
                ei = si + 64
                while(ld - ei > 64):
                    ei = ei + 64
                    stop = True
                    for x in annData[ei-64:ei]:
                        if(x in sc):
                            stop = False
                            break
                    if(stop):
                        break
                    
                if(ld - ei > 12):
                    ei = ei + 12
                else:
                    ei = ld-1
                    
                if(ei-si < minSeg):
                    d = ei - si
                    if(si > d):
                        si = si-d
                    else:
                        si = 0
                        if(ei<minSeg):
                            ei = minSeg

                # print(' - found interval ({}, {}) with {} frames'.format(si, ei, ei-si))
                if(save):
                    #save interval
                    cutFinalTrainingSegment(videoFile, posFile, annFile, si, ei-si, outFolder)
                for x in annData[si:ei]:
                    result[x] = result[x] + 1
        
                # print(' - - ann of selected interval is: ', result)
                
                finalResult = finalResult + result
                
                
                si = ei - 4
                stop = True
                for i in range(len(annData[si:])):
                    x = annData[i+si]
                    if(x in sc):
                        stop = False
                        si = si + i - 4
                        break
                if(stop):
                    break
            else:
                break
    else:
        minSeg = 100
        if(max(crtAnnSet) > sum(crtAnnSet) - 4):
            pMax = np.argmax(crtAnnSet)
            si = 0
            ei = 0
            
            if(totalAnn[pMax] > 2 * np.mean(totalAnn) ):
                si = randint(int(ld/4), int(ld/3))
                ei = si + 2 * minSeg
            elif(totalAnn[pMax] > np.mean(totalAnn)):
                si = randint(int(ld/4), int(ld/3))
                ei = randint(int(ld/3), int(ld/2))
                if(ei - si < minSeg):
                    ei = si + minSeg
            else:
                si = randint(int(ld/4), int(ld/3))
                ei = randint(int(ld/2), int(2*ld/3) )

                if(save):
                    #save interval
                    cutFinalTrainingSegment(videoFile, posFile, annFile, si, ei-si, outFolder)
                    
                result = np.zeros(noClasses)
                
                for x in annData[si:ei]:
                    result[x] = result[x] + 1

                finalResult = finalResult + result
                
                si = randint(int(ld/3), int(ld/2))
                ei = randint(int(2*ld/3), int(3*ld/4))
                
            if(save):
                #save interval
                cutFinalTrainingSegment(videoFile, posFile, annFile, si, ei-si, outFolder)
                
            result = np.zeros(noClasses)

            for x in annData[si:ei]:
                result[x] = result[x] + 1
                
            # print(' ({}, {}) with {} frames'.format(si, ei, ei-si))
            # print(' random selected interval is: ', result)#, ', crt ann set: ', crtAnnSet)
            finalResult = finalResult + result
        else:
            si = -1
            ei = 0
            
            pMax = np.argmax(crtAnnSet)
            m = 500 #max added frames
            off = 12
            
            if(totalAnn[pMax] > maxAnn):
                off = 4
            if(totalAnn[pMax] > 2 * np.mean(totalAnn)):
                m = 200
                off = 4
            elif(totalAnn[pMax] > np.mean(totalAnn)):
                m = 500
            else:
                m = 2000
                off = 40

            for i in range(len(annData)):
                x = annData[i]
                if(x != pMax and x > 0):
                    if(ld - i > 64):
                        # #avoid bad/too short annotations
                        # if(annData[i+1] == x and annData[i+2] == x and annData[i+3] == x and annData[i+4] == x):
                        if (i > off):
                            si = i - off
                        else:
                            si = 0
                        break
            if(si >= 0):
                while(True):
                    result = np.zeros(noClasses)
                    # print('select interval with searched behaviors')
                    if(ld - si > 64):
                        ei = si + 64
                        while(ld - ei > 64):
                            ei = ei + 64
                            stop = True
                            for x in annData[ei-64:ei]:
                                # if(x != pMax and totalAnn[x] < np.mean(totalAnn)):
                                if(x in sc):
                                    stop = False
                                    break
                            if(stop):
                                break
                            
                        if(ld - ei > off):
                            ei = ei + off
                        else:
                            ei = ld-1
                        
                        if(ei-si < minSeg):
                            d = ei - si
                            csi = si
                            cei = ei
                            if(ei + d < ld):
                                cei = ei+d
                            else:
                                csi = ld - minSeg
                                
                            # print(' - MAX - found interval ({}, {}) with {} frames'.format(si, ei, ei-si))
                            if(save):
                            #save interval
                                cutFinalTrainingSegment(videoFile, posFile, annFile, csi, cei-csi, outFolder)
                            
                            for x in annData[csi:cei]:
                                result[x] = result[x] + 1
                                
                            finalResult = finalResult + result
                        else:                        
                            # print(' - MAX - found interval ({}, {}) with {} frames'.format(si, ei, ei-si))
                            if(save):
                                #save interval
                                cutFinalTrainingSegment(videoFile, posFile, annFile, si, ei-si, outFolder)
        
                            for x in annData[si:ei]:
                                result[x] = result[x] + 1
                        
                            # print(' - - ann of selected interval is: ', result)
                            
                            finalResult = finalResult + result
                        si = ei #+ 64
                    else:
                        break
                    
                    stop = True
                    for i in range(len(annData[si:])):
                        x = annData[i+si]
                        # if(x != pMax and totalAnn[x] < np.mean(totalAnn)):
                        if(x in sc):
                            stop = False
                            si = si + i - off
                            break
                    if(stop):
                        break
                    
                    if(sum(finalResult) > m):
                        break

               
    # print('.')
    # print('for this segment selection has {} frames: {}'.format(sum(finalResult), finalResult))
    return finalResult
    
    
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
                '09_20180418_1200.mkv', '09_20180419_0000.mkv', '09_20180420_0000.mkv',
                '10_20180418_1800.mkv', '10_20180419_1200.mkv', '10_20180420_0000.mkv', '10_20180420_0600.mkv']
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


def addExtra(videoFile, posFile, annFile, outFolder, ann, maxIntLen, save):
    annData = getAnnData(annFile)
    ld = len(annData)
    crtAnnSet = np.zeros(noClasses)
    minSeg = 140
    maxAnn = 25000

    # check minimum interval > 64
    if (ld < minSeg):
        print('ann data segment is too short')
        return crtAnnSet

    for x in annData:
        crtAnnSet[x] = crtAnnSet[x] + 1

    sc = ann

    si = -1
    ei = 0
    finalResult = np.zeros(noClasses)

    pMax = np.argmax(crtAnnSet)

    si = searchFirst(crtAnnSet, annData, sc)
    if(si < ld - 1000):
        skipF = randint(si + 500, ld-200)
        skipAnn = annData[si+skipF:]
        skipAnnSet = np.zeros(noClasses)
        for x in skipAnn:
            skipAnnSet[x] = skipAnnSet[x] + 1
        skipI = searchFirst(skipAnnSet, skipAnn, sc)
        if(skipI > 0):
            si = si + skipF + skipI
        else:
            si = -2

    if (si >= 0):
        if (si > 4):
            si = si - 4
        else:
            si = 0

        result = np.zeros(noClasses)
        # print('select interval with searched behaviors')
        if (ld - si > 64):
            ei = si + 64
            while (ld - ei > 64):
                ei = ei + 64
                stop = True
                for x in annData[ei - 64:ei]:
                    if (x in sc):
                        stop = False
                        break
                if (stop or ei-si > maxIntLen):
                    break

            if (ld - ei > 12):
                ei = ei + 12
            else:
                ei = ld - 1

            if (ei - si < minSeg):
                d = ei - si
                if (si > d):
                    si = si - d
                else:
                    si = 0
                    if (ei < minSeg):
                        ei = minSeg

            print(' - found interval ({}, {}) with {} frames'.format(si, ei, ei-si))
            if (save):
                # save interval
                cutFinalTrainingSegment(videoFile, posFile, annFile, si, ei - si, outFolder)
            for x in annData[si:ei]:
                result[x] = result[x] + 1

            # print(' - - ann of selected interval is: ', result)

            finalResult = result

    return finalResult

if __name__ == "__main__":
        
    outFolder = '/home/andrei/Videos/train_orig'
    
    intervals_PCRS = [[0, 7500], [45000, 52500], [90000, 97500], [135000, 142500], [180000, 187500], [225000, 232500],
                      [270000, 277500], [315000, 322500], [360000, 367500], [405000, 412500], [450000, 457500], [495000, 502500]]
    # intervals_RS = [[1, 7500], [270000, 277500]]
    noClasses = 10
    inputFiles = getOriginalFiles_PCRS()    
    totalAnn = np.zeros(noClasses)

    for x in inputFiles:
        # print('select ann intervals for ', x)
        for crtInt in intervals_PCRS:
            segVideo, segAnn = cutOiginalTrainingSegment(x[0], x[1], crtInt[0], crtInt[1] - crtInt[0])
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
