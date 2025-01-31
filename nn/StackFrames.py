#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: Andrei Istudor     andrei.istudor@gmail.com
"""
*StackFrames* - Helper module containing methods that stack 
single channel frames into one multiple channel image
"""

import numpy as np
import torch

from random import randint, random
from scipy import stats



def getTestTensors(x, step=4):
    '''
    Computes tensors for processing/testing. Every 6th image in ``x`` is stacked together 
    with the 5 five previous and the 5 following following images to form a new 11 channel image.
    A `torch.Tensor` is created from the array containing these new images.
    
    If cuda is available, the data is also copied to cuda memory.
    
    :param x: input frames, single channel
    :type x: array
    :return: tensor containing the stacked images
    :rtype: torch.Tensor

    '''
    n = len(x) #64
    # lp = pos[0].shape
    b = 6
    # b2 = int(b/2)
    bins = int((n-b)/step) - 1
    
    outi = np.array(np.zeros((bins, 2*b-1, 256, 256)))
    
    # print('input shape: ', input.shape)
    
    for i in range(bins):
        ii = i * step + b - 1
    
        cs = np.stack(x[ii-b+1:ii+b:])
        outi[i] = cs
    
       
    xt = torch.from_numpy(outi)
    
    xt = xt.float()
    if torch.cuda.is_available():
        xt = xt.cuda()
    
    return xt
    
def getTensors(x, ann=None, modify=False, step=3):
    '''
    Compute tensors for training. Every 8th image in ``x`` is stacked together 
    with the 5 five previous and the 5 following following images to form a new 11 channel image.
    A `torch.Tensor` is created from the array containing these new images.
    
    If ``modify`` is True, some geometric transformations will be applied to 80% of the stacked images. 
    This helps the training process.
    
    If annotation data is provided, a similar process occurs here too. For every 8th annotation, 
    the 5 previous and the 5 following annotations are also considered. The dominant
    annotation in the set is selected, the one in the middle is prefered when there is a tie.
    This way the very short/noisy annotation events are ignored.
    A `torch.Tensor` is created from the array containing these new annotations.
    
    If cuda is available, the data is also copied to cuda memory.
    
    :param x: input frames, single channel
    :type x: array
    :param ann: annotation data, defaults to None
    :type ann: array, optional
    :param modify: True value triggers geometric altering of the image data, defaults to False
    :type modify: bool, optional
    :return: a tensor containing the stacked images and one containing the annotation tensor, or None
    :rtype: torch.Tensor, torch.Tensor

    '''

    n = len(x) 
    # lp = pos[0].shape
    b = 6
    # step = 2
    # b2 = int(b/2)
    bins = int((n-b)/step) - 1
#        print('work with n={}, b={}, bins={}'.format(n, b, bins))
    
    outi = np.array(np.zeros((bins, 2*b-1, 256, 256)))
    # outdi = np.array(np.zeros((bins, 4, 256, 256)))
    # outp = np.array(np.zeros((bins, lp[0])))
    outa = np.zeros(bins, dtype=int)
    
    # print('input shape: ', input.shape)
    
    for i in range(bins):
        ii = i * step + b - 1
        # print('ii = {}, i = {}'.format(ii, i))
        if ann is not None:
            annL = ann.tolist()
            
            aa = annL[ii-b+3:ii+b-2]
            aaf = annL[ii-b+1:ii+b]
            av = ann[ii]
            am = max(aa, key=aa.count)
            # am = stats.mode(aaf)[0][0]
            if(av != am and aa.count(am) > aa.count(av) + 1):
                amc = aaf.count(am)
                axc = aaf.count(av)
                if (amc > axc+2):
                    # print('change train ann from {} to {} in array: {}, extended: {}'.format(av, am, aa, aaf))
                    av = am
            outa[i] = av
            # outa[i-skipped] = ann[ii]
            
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

       
    xt = torch.from_numpy(outi)

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

def getTensorsBin(x, ann=None, pad=6, binPad=2, modify=False):
    # outi = np.array(np.zeros((1, 2*b-1, 256, 256)))
    # outa = np.zeros(bins, dtype=np.long)

    for i in range(pad, len(x) - pad, binPad):
        print('stack')
        #TODO: same as the old one, mostly
        #stack frames
        #compute ann
        
if __name__ == '__main__':
    print("StackFrames:")
        
