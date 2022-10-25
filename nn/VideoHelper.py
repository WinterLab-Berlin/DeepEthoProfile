#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 11:54:23 2021

@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""
import cv2
from os import path, remove
import pandas as pd
from random import randint

def cutVideo(videoFile, outVideoFile, startIndex, noFrames, scale=False):
    videoCap = cv2.VideoCapture(videoFile)
    
    if (videoCap.isOpened() == False): 
        print("Error opening video file")
        return False
    
    totalFrames = int(videoCap.get(cv2.CAP_PROP_FRAME_COUNT))
    if(startIndex > 0 and startIndex + noFrames > totalFrames):
        print('video index/number of frames is out of range')
        return False
    
    crtIndex = 0
    
    fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
    fps = videoCap.get(cv2.CAP_PROP_FPS)
    w  = int(videoCap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h  = int(videoCap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if scale:
        outW = 256
        outH = 256
    else:
        outW = w
        outH = h
        
    outVideo = cv2.VideoWriter(outVideoFile, fourcc, fps, (outW, outH))

    while(crtIndex < startIndex):
#TODO: replace OpenCV video code with something better/faster: ffmpeg-python, pyAV...
        videoCap.grab()
        crtIndex = crtIndex + 1
        
    top = randint(50, 350)
    bottom = 400 - top
    
    for i in range(noFrames):
        ret, crtFrame = videoCap.read()
        if ret:
            if scale:
                cropFrame = crtFrame[100:404, 0:w]
                
                borderIm = cv2.copyMakeBorder(cropFrame, top, bottom, 0, 0, cv2.BORDER_CONSTANT, None, [0,0,0])
                crtFrame = cv2.resize(borderIm, (256, 256), interpolation = cv2.INTER_AREA)
            outVideo.write(crtFrame)
        else:
            print('error reading video')
            outVideo.release()
            if(path.exists(outVideoFile)):
                remove(outVideoFile)
                
            return False
        
    outVideo.release()
    return True

def cutAnnFile(annFile, outputFile, startIndex, noFrames):
    # if(path.exists(outputFile)):
    #     print('crop ann file already exists, nothing to do')
    #     return True
    
    annDataPD = pd.read_csv(annFile, sep=';', header=1)
    
    cutFile = open(outputFile, 'w')
    cutFile.write('0:none; 1:drink; 2:eat; 3:groom back; 4:groom; 5:hang; 6:micromovement; 7:rear; 8:rest; 9:walk; \n')
    
    annData = annDataPD.loc[startIndex:startIndex + noFrames, 'frame':'annotation']
    annData.to_csv(cutFile, sep=';', index=False, mode='a')
    
    cutFile.close()

    return True
        
def cutPosFile(posFile, outputFile, startIndex, noFrames):
# if(path.exists(outputFile)):
#     print('crop pos file already exists, nothing to do')
#     return True
    posFileS = open(posFile, 'r')
    cutFile = open(outputFile, 'w')
    
    #read first two lines - cage position data
    cutFile.write(posFileS.readline())
    cutFile.write(posFileS.readline())
    
    posFileS.close()

    posDataPD = pd.read_csv(posFile, sep=';', header=2)

    posFeatures = posDataPD.loc[startIndex:startIndex + noFrames, 'frame':'rightDist']
    posFeatures.to_csv(cutFile, sep=';', index=False, mode='a')
    
    cutFile.close()
    
    return True


def cutFinalTrainingSegment(videoFile, annFile, startIndex, noFrames, outputFolder): #posFile
    if(path.exists(videoFile) and path.exists(annFile)): #
        outExt = '_s{}_n{}'.format(startIndex, noFrames)
        outVideoFile = videoFile.replace('.avi', outExt + '.avi')
        # outPosFile = videoFile.replace('.avi', outExt + '_pos.csv')
        outAnnFile = videoFile.replace('.avi', outExt + '_ann.csv')
        
        if(outputFolder is not None):
            outVideoFile = path.basename(outVideoFile)
            # outPosFile = path.basename(outPosFile)
            outAnnFile = path.basename(outAnnFile)
            
            outVideoFile = path.join(outputFolder, outVideoFile)
            # outPosFile = path.join(outputFolder, outPosFile)
            outAnnFile = path.join(outputFolder, outAnnFile)
            
        if(path.exists(outVideoFile) and path.exists(outAnnFile)): #and path.exists(outPosFile) 
            # print('cropped files already exist')
            return outVideoFile, outAnnFile #
        else:
            # print('crop file {} from index {}'.format(videoFile, startIndex))
            if(cutVideo(videoFile, outVideoFile, startIndex, noFrames) and
                cutAnnFile(annFile, outAnnFile, startIndex, noFrames)):
                #     and 
                # cutPosFile(posFile, outPosFile, startIndex, noFrames)):
                
                return outVideoFile, outAnnFile #
            
    return None, None #, None

def cutTrainingSegment(videoFile, posFile, annFile, startIndex, noFrames):
    if(path.exists(videoFile) and path.exists(posFile) and path.exists(annFile)):
        outExt = '_s{}_n{}'.format(startIndex, noFrames)
        outVideoFile = videoFile.replace('.avi', outExt + '.avi')
        outPosFile = posFile.replace('.csv', outExt + '.csv')
        outAnnFile = annFile.replace('.csv', outExt + '.csv')
        
        if(path.exists(outVideoFile) and path.exists(outPosFile) and path.exists(outAnnFile)):
            # print('cropped files already exist')
            return outVideoFile, outPosFile, outAnnFile
        else:
            print('crop file: ', videoFile)
            if(cutVideo(videoFile, outVideoFile, startIndex, noFrames) and
                cutAnnFile(annFile, outAnnFile, startIndex, noFrames) and 
                cutPosFile(posFile, outPosFile, startIndex, noFrames)):
                
                return outVideoFile, outPosFile, outAnnFile
            
    return None, None, None


def cutOiginalTrainingSegment(videoFile, annFile, startIndex, noFrames):
    if(path.exists(videoFile) and path.exists(annFile)):
        outExt = '_s{}_n{}'.format(startIndex, noFrames)
        outVideoFile = videoFile.replace('.avi', outExt + '.avi')
        # outPosFile = posFile.replace('.csv', outExt + '.csv')
        outAnnFile = annFile.replace('.csv', outExt + '.csv')
        
        if(path.exists(outVideoFile) and path.exists(outAnnFile)): #and path.exists(outPosFile) 
            # print('cropped files already exist')
            return outVideoFile, outAnnFile #outPosFile, 
        else:
            print('crop file: ', videoFile)
            if(cutVideo(videoFile, outVideoFile, startIndex, noFrames, False) and
                cutAnnFile(annFile, outAnnFile, startIndex, noFrames)):
                # and 
                # cutPosFile(posFile, outPosFile, startIndex, noFrames)):
                
                return outVideoFile, outAnnFile #outPosFile, 
            
    return None, None

def cutOiginalTrainingSegment_Crop(videoFile, annFile, startIndex, noFrames):
    if(path.exists(videoFile) and path.exists(annFile)):
        outExt = '_s{}_n{}'.format(startIndex, noFrames)
        outVideoFile = videoFile.replace('.avi', outExt + '.avi')
        # outPosFile = posFile.replace('.csv', outExt + '.csv')
        outAnnFile = annFile.replace('.csv', outExt + '.csv')
        
        if(path.exists(outVideoFile) and path.exists(outAnnFile)): #and path.exists(outPosFile) 
            # print('cropped files already exist')
            return outVideoFile, outAnnFile #outPosFile, 
        else:
            print('crop file: ', videoFile)
            if(cutVideo(videoFile, outVideoFile, startIndex, noFrames, False) and
                cutAnnFile(annFile, outAnnFile, startIndex, noFrames)):
                # and 
                # cutPosFile(posFile, outPosFile, startIndex, noFrames)):
                
                return outVideoFile, outAnnFile #outPosFile, 
            
    return None, None
        

if __name__ == "__main__":
    dataFolder = '/home/andrei/Videos/validation/20180418_BL_WT'
    annFolder = '/home/andrei/Videos/validation/20180418_BL_WT/ann_train'

    videoFiles = ['01_20180418_1200.mkv_fg.avi'] #, '01_20180418_1800.mkv_fg.avi', '01_20180420_0600.mkv_fg.avi',
              # '02_20180418_1800.mkv_fg.avi',
              # '08_20180418_1200.mkv_fg.avi', '08_20180418_1800.mkv_fg.avi', '08_20180419_0000.mkv_fg.avi',
              # '09_20180418_1200.mkv_fg.avi', '09_20180419_0000.mkv_fg.avi', '09_20180420_0000.mkv_fg.avi',  
              # '10_20180420_0000.mkv_fg.avi', '10_20180420_0600.mkv_fg.avi']

    annFiles = ['01_20180418_1200_RS.csv'] #,  '01_20180418_1800_RS.csv', '01_20180420_0600_PC.csv',
            # '02_20180418_1800_RS.csv',
            # '08_20180418_1200_RS.csv', '08_20180418_1800_RS.csv', '08_20180419_0000_RS.csv', 
            # '09_20180418_1200_PC.csv', '09_20180419_0000_RS.csv', '09_20180420_0000_RS.csv', 
            # '10_20180420_0000_PC.csv', '10_20180420_0600_RS.csv']


    for i in range(len(videoFiles)):
        crtVideoFile = videoFiles[i]
        crtPosFile = crtVideoFile.replace('.avi', '.csv')
        crtAnnFile = annFiles[i]
        
        annFile = path.join(annFolder, crtAnnFile)
        videoFile = path.join(dataFolder, crtVideoFile)
        posFile = path.join(dataFolder, crtPosFile)
        
        newVideoFile, newPosFile, newAnnFile = cutTrainingSegment(videoFile, posFile, annFile, 0, 100)
        
        print(newVideoFile)
        print(newPosFile)
        print(newAnnFile)
        

        
