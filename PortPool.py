#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Andrei Istudor
"""

from threading import Lock

class PortPool:
    def __init__(self, noPorts):
        self.portPool = {}
        self.poolLock = Lock()

        with self.poolLock:
            for i in range(noPorts):
                self.portPool[i] = 0

    def getPort(self):
        with self.poolLock:
            for i in range(len(self.portPool)):
                if self.portPool[i] == 0:
                    self.portPool[i] = 1
                    return i
        return -1

    def resetPort(self, i):
        with self.poolLock:
            if i >= 0 and i < len(self.portPool):
                self.portPool[i] = 0


