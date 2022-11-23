#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""

from threading import Lock

class PortPool:
    '''
    Class implementing a single access list for managing the allocation of communication ports with the processing instances. 
    
    On construction a list of size `noPorts` is created and initialized to 0, meaning all ports are avaialble. 
    
    :param noPorts: the number of ports available for the application
    :type noPorts: int
    '''
    
    #: internal array corresponding to the total number of ports and their availability
    portPool: []
    
    def __init__(self, noPorts):
        self.portPool = {}
        self.poolLock = Lock()

        with self.poolLock:
            for i in range(noPorts):
                self.portPool[i] = 0

    def getPort(self):
        '''
        Checks the :data:`portPool` for an entry of 0, meaning available. 
        The index of the first one found is returned. 
        If none is found, the method returns -1, meaning all ports are already acquired.

        :return: a new positive number if a port is available or -1
        :rtype: int

        '''
        with self.poolLock:
            for i in range(len(self.portPool)):
                if self.portPool[i] == 0:
                    self.portPool[i] = 1
                    return i
        return -1

    def resetPort(self, portId):
        '''
        Resets the entry in :data:`portPool` at index :data:`portId` so that it can be acquired through a subsequent call to :func:`getPort`
        
        :param portId: the id of the port to be reset
        :type portId: int

        '''
        with self.poolLock:
            if portId >= 0 and portId < len(self.portPool):
                self.portPool[portId] = 0


