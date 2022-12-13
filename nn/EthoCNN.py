#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defines the CNN that performs the classification


@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch.nn import Linear, ReLU, CrossEntropyLoss, Sequential, Conv2d, MaxPool2d, Module, Softmax, BatchNorm2d, Dropout
from torch.optim import Adam, SGD

from scipy import stats
from random import randint, random

class EthoCNN(nn.Module):
    '''
    The implmentation of the CNN to each annotate stacked image with the corresponding behaviour. 
    The algorithm is designed to function robustly in the context of low distinctive features of the mouse and potential big changes of the environment.
   
    The images used here have 11 channels corresponding to 11 frames, and are typically obtained with the help of the methods from :mod:`StackFrames`
    This transforms movement features into image features that are more relevant to behaviour and easier to classify.
    
    The structure is similar to the one from the image classification proposed by Krizhevsky et al. in ImageNet.
    One major difference (apart from the number of channels) is that the first convolution layer is formed by 4 asymetrical filters that will react
    differently to various movement patterns. 
    '''
    
    #: numer of classes in which the image will be classified
    noClasses: int
    
    #: size of the fully connected layer = 4096
    fc_size: int
    
    #: size of the last convolution layer = 8
    cf_s: int #8
    
    #: number of channels of the last convolution layer
    cf_n: int #256
    
    #: normalization layer for the input image N(11 channels)
    bn1: nn.BatchNorm2d 
    
    #: first filter of the first convolution layer: C(11, 64, (11, 1), padding=(5,0), stride=2)
    c11: nn.Conv2d
    
    #: second filter of the first convolution layer: C(11, 64, (1, 11), padding=(0,5), stride=2)
    c12: nn.Conv2d 

    #: third filter of the first convolution layer: C(11, 64, (7, 3), padding=(3,1), stride=2)
    c13: nn.Conv2d 

    #: fourth filter of the first convolution layer: C(11, 64, (3, 7), padding=(1,3), stride=2)
    c14: nn.Conv2d 
    
    #: second convolution layer: C(256, 384, 7, stride=2)
    c2: nn.Conv2d  # need to compromise for the mem
    
    #: third convolution layer: C(384, 512, 5)
    c3: nn.Conv2d #
    
    #: fourth convolution layer: C(512, self.cf_n, 3)
    c4: nn.Conv2d #
    
    #: dropout layer
    dropout: nn.Dropout #(0.5)
    
    #: first fully connected layer to transform the output of the convolution layers FC(self.cf_s * self.cf_s * self.cf_n, self.fc_size)
    fc1: nn.Linear #
    
    #: second fully connected layer to obtain the final classification: FC(self.fc_size, self.noClasses)
    fc2: nn.Linear #
    
    def __init__(self, noClasses):
        super(EthoCNN, self).__init__()
        
        self.noClasses = noClasses
        
        #deprecated, not used anymore
        self.noPosFeatures = 0 #24 #32 #28

        self.fc_size = 4096
        self.cf_s = 8
        self.cf_n = 256
        
        self.bn1 = nn.BatchNorm2d(11, track_running_stats=False)
        self.c11 = nn.Conv2d(11, 64, (11, 1), padding=(5,0), stride=2)
        self.c12 = nn.Conv2d(11, 64, (1, 11), padding=(0,5), stride=2)
        self.c13 = nn.Conv2d(11, 64, (7, 3), padding=(3,1), stride=2)
        self.c14 = nn.Conv2d(11, 64, (3, 7), padding=(1,3), stride=2)
        
        #deprecated, not used anymore
        self.bn2 = nn.BatchNorm2d(256, track_running_stats=False)
        
        self.c2 = nn.Conv2d(256, 384, 7, stride=2) # need to compromise for the mem
        self.c3 = nn.Conv2d(384, 512, 5)
        self.c4 = nn.Conv2d(512, self.cf_n, 3)

        self.dropout = nn.Dropout(0.5)
        
        #2 fully connected layers to transform the output of the convolution layers to the final output
        self.fc1 = nn.Linear(self.cf_s * self.cf_s * self.cf_n, self.fc_size)
        self.fc2 = nn.Linear(self.fc_size, self.noClasses) #


    def forward(self, x):
        '''
        Implements the architecture of the CNN as:
            
        bn1-[c11, c12, c13, c14]-P(3,2)-c2-P(3,2)-c3-c4-dropout-fc1-dropout-fc2
        
        After an initial batch normalization, the 4 convolutions of the first layer are applied to the normed input.
        The results are stacked and then 2D max pooling is applied on the resulting tensor.
        Another 2D max pooling is applied after the second layer convolution.
        Each convolution layer is followed by a Rectified Linear Unit (ReLU).
        A Dropout step that randomly zeroes some of the elements of the input tensor during training is applied before each fully connected layer.
        
        :param x: set of images that will be processed in parallel
        :type x: array
        :return: the log_softmax value of the classification results for each input image in :data:`x`
        :rtype: array

        '''
        
        x = self.bn1(x)
        x1 = torch.relu(self.c11(x))
        x2 = torch.relu(self.c12(x))
        x3 = torch.relu(self.c13(x))
        x4 = torch.relu(self.c14(x))
        
        # print('input filter: {}'.format(x1.shape))
        x = torch.cat((x1, x3, x4, x2), dim=1) #x1,,x2
        # print('input filter stack: {}'.format(x.shape))
        x = torch.max_pool2d(x, 3, 2)
        # print('input filter stack & pool: {}'.format(x.shape))
        
        # x = self.bn2(x)
        x = torch.relu(self.c2(x))
        # print('c2: {}'.format(x.shape))
        x = torch.max_pool2d(x, 3, 2)
        # print('c2 & pool: {}'.format(x.shape))

        x = torch.relu(self.c3(x))
        # x = torch.max_pool2d(x, 3, 2)
        # print('c3: {}'.format(x.shape))

        x = torch.relu(self.c4(x))
        # x = torch.max_pool2d(x, 3, 2)
        # print('c4: {}'.format(x.shape))

    
        # print(x.shape)
        #flatten the output for each image
        x = x.view(-1, self.cf_s * self.cf_s * self.cf_n)  # batch_size x 8*8*128
        x = self.dropout(x)
        #apply 2 fully connected layers with dropout
        x = torch.relu(self.fc1(x)) 
        x = self.dropout(x)
        x = self.fc2(x)
        # x = torch.relu(x)
    
        return torch.log_softmax(x, dim=1)

