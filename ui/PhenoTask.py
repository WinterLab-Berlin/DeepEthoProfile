#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Andrei Istudor
"""

from os import path
from PyQt5 import QtCore

from TaskState import TaskState

class PhenoTask(QtCore.QObject):
    progressQt = QtCore.pyqtSignal(int, float)
    stateQt = QtCore.pyqtSignal(int, TaskState)

    def __init__(self, id, videoPath):
        QtCore.QObject.__init__(self)
        self.videoPath = videoPath
        self.id = id
        self.state = TaskState.new
        self.progress = 0

        (h, t) = path.split(self.videoPath)
        self.dirPath = h
        self.fileName = t

        self.changed = True

    def setState(self, state):
        if state is not self.state:
            self.state = state
            self.progress = 0
            self.setChanged(True)
            #print('Task {} changed state to {}'.format(self.id, self.state))
            self.stateQt.emit(self.id, self.state)

    def setProgress(self, progress):
        self.progress = progress
        self.setChanged(True)
        #TODO: emit changed progress - for GUI
        self.progressQt.emit(self.id, self.progress)

    def getDirPath(self):
        return self.dirPath

    def getFileName(self):
        return self.fileName

    def setChanged(self, value):
        self.changed = value
    def getChanged(self):
        return self.changed


if __name__ == '__main__':
    pt = PhenoTask(1, '/home/andrei/Videos/test/short.mkv')
    print(pt.getDirPath())
    print(pt.getFileName())
