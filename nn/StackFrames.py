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
        

def getTensors(x, ann=None, modify=False): #pos, 
    n = len(x) #64
    # lp = pos[0].shape
    b = 6
    b2 = int(b/2)
    bins = int((n-b+1)/b)
    
#        print('work with n={}, b={}, bins={}'.format(n, b, bins))
    
    outi = np.array(np.zeros((bins, 2*b-1, 256, 256)))
    # outdi = np.array(np.zeros((bins, 4, 256, 256)))
    # outp = np.array(np.zeros((bins, lp[0])))
    outa = np.zeros(bins, dtype=np.long)
    
    # print('input shape: ', input.shape)
    
    for i in range(bins):
        ii = i * b + b - 1
    
        if(random() > 0.8):
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
                    im = np.flip(im, 2)
                    
                if tx:
                    if ty:
                        outi[i][crtidx][:256-sy, sx:] = im[0, sy:, :256-sx]
                    else:
                        outi[i][crtidx][sy:, sx:] = im[0, :256-sy, :256-sx]
                else:
                    if ty:
                        outi[i][crtidx][:256-sy, :256-sx] = im[0, sy:, sx:]
                    else:
                        outi[i][crtidx][sy:, :256-sx] = im[0, :256-sy, sx:]

                        

                crtidx += 1
        else:
            cs = np.stack(x[ii-b+1:ii+b, 0, :, :])
            outi[i] = cs

        if ann is not None:
            av = ann[ii]
            am = stats.mode(ann[ii-b2:ii+b2])[0][0]
            if(av != am):
                axc = 0
                for ax in ann[ii-b2:ii+b2]:
                    if(av == ax): #always stops at the middle, but that's ok
                        axc += 1
                if axc == 1:
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

