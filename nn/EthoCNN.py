#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defines the CNN that performs the classification

@author: Andrei Istudor     andrei.istudor@gmail.com
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
    The implementation of the CNN to each annotate stacked image with the corresponding behaviour.
    The algorithm is designed to function robustly in the context of low distinctive features of the mouse and potential big changes of the environment.
   
    The images used here have 11 channels corresponding to 11 monochromatic frames
    This transforms movement features into image features that are more relevant to behaviour and easier to classify.
    
    The structure is similar to the one from the image classification proposed by Krizhevsky et al. in ImageNet.
    One major difference (apart from the number of channels) is that the first convolution layer is formed by 4 asymmetrical filters that will react
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

        self.fc_size = 2048
        self.cf_s = 4
        self.cf_n = 256
        
        self.bn1 = nn.BatchNorm2d(11)
        
        self.c11 = nn.Conv2d(11, 32, (11, 1), padding=(5,0), stride=2)
        self.c12 = nn.Conv2d(11, 32, (1, 11), padding=(0,5), stride=2)
        self.c13 = nn.Conv2d(11, 32, (7, 3), padding=(3,1), stride=2)
        self.c14 = nn.Conv2d(11, 32, (3, 7), padding=(1,3), stride=2)
        
        self.bn2 = nn.BatchNorm2d(128) #, track_running_stats=False)
        self.c2 = nn.Conv2d(128, 256, 5) # need to compromise for the mem
        self.bn3 = nn.BatchNorm2d(256)
        self.c3 = nn.Conv2d(256, 384, 3)
        # self.bn4 = nn.BatchNorm2d(512)
        self.c32 = nn.Conv2d(384, 512, 3)
        self.c4 = nn.Conv2d(512, self.cf_n, 3)
        # self.bn5 = nn.BatchNorm2d(self.cf_n)

        self.dropout = nn.Dropout(0.5)
        
        #2 fully connected layers to transform the output of the convolution layers to the final output
        self.fc1 = nn.Linear(self.cf_s * self.cf_s * self.cf_n, self.fc_size)
        self.fc12 = nn.Linear(self.fc_size, self.fc_size)
        self.fc2 = nn.Linear(self.fc_size, self.noClasses) #



    def forward(self, x):
        
        x = self.bn1(x)
        x1 = torch.relu(self.c11(x))
        x2 = torch.relu(self.c12(x))
        x3 = torch.relu(self.c13(x))
        x4 = torch.relu(self.c14(x))
        
        x = torch.cat((x1, x3, x4, x2), dim=1) #x1,,x2
        x = torch.max_pool2d(x, 3, 2)
        
        x = self.bn2(x)
        x = torch.relu(self.c2(x))
        x = torch.max_pool2d(x, 3, 2)
        x = self.bn3(x)

        x = torch.relu(self.c3(x))
        x = torch.max_pool2d(x, 3, 2)
        x = torch.relu(self.c32(x))
        # x = torch.max_pool2d(x, 3, 2)
        # x = self.bn4(x)
        # x = torch.max_pool2d(x, 3, 2)

        x = torch.relu(self.c4(x))
        x = torch.max_pool2d(x, 3, 2)
        # x = self.bn5(x)

    
        # print(x.shape)
        #flatten the output for each image
        x = x.view(-1, self.cf_s * self.cf_s * self.cf_n)  # batch_size x 8*8*128
        #apply 2 fully connected layers with dropout
        x = self.dropout(x)
        x = torch.relu(self.fc1(x)) 
        x = self.dropout(x)
        x = torch.relu(self.fc12(x)) 
        x = self.fc2(x)
        # x = torch.relu(x)
    
        return x

