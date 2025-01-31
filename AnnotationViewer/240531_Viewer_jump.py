#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 20:24:25 2024

@author: Andrei Istudor     andrei.istudor@gmail.com
"""


import pandas as pd
import numpy as np
# import av
import cv2
from os import path, remove
import sys
    

def loadVideo(videoFile):
    frames = []
    cap = cv2.VideoCapture(videoFile)
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(gray)
    cap.release()
    
    return frames

def getAnn(i):
    annString = 'None'
    if(i == 0):
        annString = 'drink'
    elif(i == 1):    
        annString = 'eat'
    elif(i ==2):   
        annString = 'groom'
    elif(i == 3):    
        annString = 'hang'
    elif(i == 4):   
        annString = 'mm'
    elif(i ==5):  
        annString = 'rear'
    elif(i ==6):    
        annString = 'rest'
    elif(i ==7):    
        annString = 'walk'
    
    annString = annString + ' = ' + str(i)
    
    return annString

def saveAnn(annFile, annData, oldAnnData):
    if(path.exists(annFile)):
        print('replace ann file')
        remove(annFile)
        
    outFile = open(annFile, 'w')
    outFile.write('0:drink; 1:eat; 2:groom; 3:hang; 4:micromovement; 5:rear; 6:rest; 7:walk; \n')
    outFile.write('frame;annotation\n')
    
    for index, row in oldAnnData.iterrows():
        frame = row['frame']
        newAnn = annData[index]
        outFile.write(str(frame) + ';' + str(newAnn) + '\n')

    outFile.close()
    print('save file: ', annFile)

    
def displayFrame(frame, frameNo, ann, newAnn):
    annText = getAnn(ann)
    newAnnText = getAnn(newAnn)
    
    cv2.rectangle(frame, (0, 0), (256, 40), (10,10,10), -1)
    cv2.putText(frame, annText + ' _ frame=' + str(frameNo), (5, 24), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (220,255,220), 1);

    cv2.rectangle(frame, (0, 600), (704, 704), (10,10,10), -1)
    cv2.putText(frame, newAnnText, (5, 620), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (220,255,220), 1);

    cv2.imshow('frame', frame)
    
    cv2.setWindowProperty('frame', 1, cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', 700, 700)
    
def getAnnKey(key):
    ann = -1
    
    if(key  == ord('0')):
        ann = 0
    elif(key  == ord('1')):
        ann = 1
    elif(key  == ord('2')):
        ann = 2
    elif(key== ord('3')):
        ann = 3
    elif(key  == ord('4')):
        ann = 4
    elif(key  == ord('5')):
        ann = 5
    elif(key  == ord('6')):
        ann = 6
    elif(key  == ord('7')):
        ann = 7
    
    return ann



def playVideo(frames, annData, newAnnData, spd, outAnnFile):
    i = 0
    dir = 0
    paused = False
	
    cv2.namedWindow("frame", cv2.WINDOW_NORMAL) 
	
    while(True):
        if(i<0):
            i=0
            paused = True
        
        if(i>=len(frames)):
            paused = True
            saveAnn(outAnnFile, newAnnData, annData)
            break

        x = frames[i]
        crtAnn = int(annData.loc[i, 'annotation'])
        newAnn = newAnnData[i]
        
        displayFrame(x, i, crtAnn, newAnn)        

        if(paused):
            sKey = cv2.waitKey()
            if(sKey  == ord(' ')):
                paused = False
                saveAnn(outAnnFile, newAnnData, annData)
                continue
            
            if(sKey == ord('b')):
                i -= 1
                continue
            
            if(sKey == ord('n')):
                i += 1
                dir = 0
                continue
            newAnn = getAnnKey(sKey)
            if(newAnn >= 0):
                newAnnData[i] = newAnn
                i += 1
                
            if(sKey  == ord('q')):
                saveAnn(outAnnFile, newAnnData, annData)
                break
            if(sKey  == ord('w')):
                saveAnn(outAnnFile, newAnnData, annData)
                
            if(sKey == ord('j')):
                lisfra = []
                while(True):
                    sKey = cv2.waitKey()

                    if(sKey == ord('t')):
                        break

                    if(sKey >= 48 and sKey <= 57):
                        lisfra.append(sKey-48)
                        print(lisfra)
                    else:
                        print('Choose a number')

                if(len(lisfra)) == 0:
                   print('No number given.')
                   continue

                k = ''
                for numbers in lisfra:
                    k = k + str(numbers)

                if(int(k) >= len(frames)):
                    print('Frame outside of video: ', k)
                else:
                    i = int(k)
                
            continue

        else:
            key = cv2.waitKey(spd)
            if(key  == ord('q')):
                saveAnn(outAnnFile, newAnnData, annData)
                break
            
#            if(key  == ord('d')):
 #               if(dir == 0):
  #                  dir = 1
   #             else:
    #                dir = 0
     #           continue
            
            if(key  == ord('s')):
                spd += 40
                continue
                
            if(key  == ord('f')):
                spd -= 40
                if(spd < 40): spd = 40
                continue
            
            if(key  == ord(' ')):
                paused = True
                continue
            
#            if(dir == 0):
            i += 1
 #           else:
  #              i -= 1
                
#            if(i < 0):
 #               i = 0
  #              dir = 0
                
            if(i >= len(frames)):
            	saveAnn(outAnnFile, newAnnData, annData)
            	paused = True
#                i = len(frames)
 #               dir = 1
            
    
    
    if cv2.waitKey(100) == ord('q'):
        print('quit')

    cv2.destroyAllWindows()
    
def annotateVideo(videoFile, annFile, spd):
    newAnnData = []
    annData = []
    
    outAnnFile = annFile.replace('.csv', '_new.csv')
    
    if(path.exists(outAnnFile)):
        newAnnDF = pd.read_csv(outAnnFile, sep=';', header=1)
        annData = pd.read_csv(outAnnFile, sep=';', header=1)
        for x in newAnnDF['annotation']:
            newAnnData.append(x)
    else:
        annData = pd.read_csv(annFile, sep=';', header=1)
        for x in annData['annotation']:
            newAnnData.append(x)
    
    frames = loadVideo(videoFile)
    print('loaded video')
    
    playVideo(frames, annData, newAnnData, spd, outAnnFile)

if __name__ == "__main__":
    videoFile = '01_20180418_1200_s45000_n7500.avi'
    annFile = '01_20180418_1200_s45000_n7500_map.csv'
    
    if (len(sys.argv) > 1):
        annFile = sys.argv[1]
        videoFile = annFile.replace('_map.csv', '.avi')
        print('video = ', videoFile)
    else:
        print ('using video: ', videoFile)
        
    finished = False
    spd = 40
    
    annotateVideo(videoFile, annFile, spd)

