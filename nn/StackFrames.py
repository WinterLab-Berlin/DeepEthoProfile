#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 17:16:32 2022

@author: Andrei Istudor
"""


import numpy as np
import torch

from random import randint, random
from scipy import stats


def getTesnsorsBin(x, ann=None, pad=6, binPad=2, modify=False):
    # outi = np.array(np.zeros((1, 2*b-1, 256, 256)))
    # outa = np.zeros(bins, dtype=np.long)

    for i in range(pad, len(x) - pad, binPad):
        print('stack')
        #TODO: same as the old one, mostly
        #stack frames
        #compute ann
        
def getTestTensors(x):
    n = len(x) #64
    # lp = pos[0].shape
    b = 6
    b2 = int(b/2)
    bins = int((n-b+1)/b)
    
    outi = np.array(np.zeros((bins, 2*b-1, 256, 256)))
    
    # print('input shape: ', input.shape)
    
    for i in range(bins):
        ii = i * b + b - 1
    
        cs = np.stack(x[ii-b+1:ii+b:])
        outi[i] = cs
    
       
    xt = torch.from_numpy(outi)
    
    xt = xt.float()
    if torch.cuda.is_available():
        xt = xt.cuda()
    
    return xt
    


def getTensors(x, ann=None, modify=False): #pos, 
    n = len(x) 
    # lp = pos[0].shape
    b = 6
    step = 8
    b2 = int(b/2)
    bins = int((n-b+1)/step)
    
#        print('work with n={}, b={}, bins={}'.format(n, b, bins))
    
    outi = np.array(np.zeros((bins, 2*b-1, 256, 256)))
    # outdi = np.array(np.zeros((bins, 4, 256, 256)))
    # outp = np.array(np.zeros((bins, lp[0])))
    outa = np.zeros(bins, dtype=np.long)
    
    # print('input shape: ', input.shape)
    
    for i in range(bins):
        ii = i * step + b - 1
    
        if(random() > 0.9):
            modify = False
            
        if(modify):
            crtidx = 0
            sx = randint(0, 10)
            sy = randint(0, 55)
            flip = False
            tx = True
            ty = True
            if(random() > 0.8):
                flip = True
            if(random() > 0.5):
                tx = False
            if(random() > 0.5):
                ty = False
                
            for im in x[ii-b+1:ii+b]:
                # print('change im')
                
                if flip:
                    im = np.flip(im, 1)
                    
                if tx:
                    if ty:
                        outi[i][crtidx][:256-sy, sx:] = im[sy:, :256-sx]
                    else:
                        outi[i][crtidx][sy:, sx:] = im[:256-sy, :256-sx]
                else:
                    if ty:
                        outi[i][crtidx][:256-sy, :256-sx] = im[sy:, sx:]
                    else:
                        outi[i][crtidx][sy:, :256-sx] = im[:256-sy, sx:]

                        

                crtidx += 1
        else:
            cs = np.stack(x[ii-b+1:ii+b:])
            outi[i] = cs

        if ann is not None:
            # av = ann[ii]
            # am = stats.mode(ann[ii-b2:ii+b2])[0][0]
            # if(av != am):
            #     axc = 0
            #     for ax in ann[ii-b2:ii+b2]:
            #         if(av == ax): #always stops at the middle, but that's ok
            #             axc += 1
            #     if axc == 1:
            #         print('replace ann {} with {} in set {}'.format(av, am, ann[ii-b2:ii+b2]))
            #         av = am
            annL = ann.tolist()
                    
            
            aa = annL[ii-b+3:ii+b-2]
            aaf = annL[ii-b+1:ii+b]
            av = ann[ii]
            am = max(aa, key=aa.count)
            # am = stats.mode(aaf)[0][0]
            if(av != am and aa.count(am) > aa.count(av) + 1):
                amc = aaf.count(am)
                axc = aaf.count(av)
                # axc = 0
                # amc = 0  
                # for ax in aa:
                #     if(av == ax): #always stops at the middle, but that's ok
                #         axc += 1
                #     elif(ax == am):
                #         amc += 1
                if (amc > axc+2):
                    print('change train ann from {} to {} in array: {}, extended: {}'.format(av, am, aa, aaf))
                    av = am
            outa[i] = av
        
        # print('input i:{} ii:{} = {}'.format(i, ii,x.shape))
       # print('input i:{} ii:{} = {}'.format(i, ii, x))
       
    xt = torch.from_numpy(outi)
    # posT = torch.from_numpy(outp)
    # posT = posT.float()

    xt = xt.float()
    if torch.cuda.is_available():
        xt = xt.cuda()
        # posT = posT.cuda()
        
    if ann is not None:
        annT = torch.from_numpy(outa)
        annT = annT.long()
        if torch.cuda.is_available():
            annT = annT.cuda()

        return xt, annT
    else:
        return xt, None

