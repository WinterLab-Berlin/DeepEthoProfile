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
    def __init__(self, noClasses):
        super(EthoCNN, self).__init__()
        
        self.noClasses = noClasses
        self.noPosFeatures = 0 #24 #32 #28

        self.fc_size = 4096
        self.cf_s = 8
        self.cf_n = 256
        
        self.bn1 = nn.BatchNorm2d(11, track_running_stats=False)
        self.c11 = nn.Conv2d(11, 64, (11, 1), padding=(5,0), stride=2)
        self.c12 = nn.Conv2d(11, 64, (1, 11), padding=(0,5), stride=2)
        self.c13 = nn.Conv2d(11, 64, (7, 3), padding=(3,1), stride=2)
        self.c14 = nn.Conv2d(11, 64, (3, 7), padding=(1,3), stride=2)
        
        self.bn2 = nn.BatchNorm2d(256, track_running_stats=False)
        self.c2 = nn.Conv2d(256, 384, 7, stride=2) # need to compromise for the mem
        self.c3 = nn.Conv2d(384, 512, 5)
        self.c4 = nn.Conv2d(512, self.cf_n, 3)

        self.dropout = nn.Dropout(0.5)
        
        #2 fully connected layers to transform the output of the convolution layers to the final output
        self.fc1 = nn.Linear(self.cf_s * self.cf_s * self.cf_n, self.fc_size)
        self.fc2 = nn.Linear(self.fc_size, self.noClasses) #


    def forward(self, x):
        # x = torch.relu(self.bn00(self.c00(x)))   
        # x = torch.max_pool2d(x, 3, 2)
        # x = torch.relu(self.bn01(self.c01(x)))
        # x = torch.max_pool2d(x, 3, 2)
        
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

