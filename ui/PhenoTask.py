#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""

from os import path
from PyQt5 import QtCore

from TaskState import TaskState

class PhenoTask(QtCore.QObject):
    '''
    Class encapsulating one video file and it's current status. 
    
    Every time a video is selected for processing a new :class:`PhenoTask` object is created. 
    The current state and the processing progress are managed here.
    The class also contains the means to propagate changes to other parts of the application. 
    
    :param id: the unique id of this task
    :type id: int
    :param videoPath: the path to the video corresponding to the current task
    :type videoPath: str
    '''
    
    #: Progress of the current operation, initialized to 0
    progress: int
    
    #: Full path to the video corresponding to this task
    videoPath: str
    
    #: Path to the directory where the video corresponding to this task is found
    dirPath: str
    
    #: File name of the video corresponding to this task
    fileName: str
    
    #: Unique id of the current task
    id: int
    
    #: The current state of this task, initialized to :data:`TaskState.new`
    state: TaskState
    
    #: Flag to check whether the contents of the task have been changed since last reset.
    changed: bool
    
    #: Signal for updating the progress of the current task
    progressQt: QtCore.pyqtSignal

    #: Signal for updating the state of the current task
    stateQt: QtCore.pyqtSignal

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
        '''
        Set the state to ``state`` of the task and activates the :data:`stateQt` signal to propagate the change.
        
        Variable :data:`progress` will be also set to 0.
        
        :param state: new state
        :type state: TaskState

        '''
        if state is not self.state:
            self.state = state
            self.progress = 0
            self.setChanged(True)
            #print('Task {} changed state to {}'.format(self.id, self.state))
            self.stateQt.emit(self.id, self.state)

    def setProgress(self, progress):
        '''
        Set the state to ``progress`` of the task to the :data:`progress` value in parameter. It also activates the :data:`progressQt` signal to propagate the change.
        
        :param progress: new progress value
        :type progress: int

        '''
        self.progress = progress
        self.setChanged(True)
        #TODO: emit changed progress - for GUI
        self.progressQt.emit(self.id, self.progress)

    def getDirPath(self):
        '''
        Returns the folder path where the video corresponding to this task is found.
        
        :return: folder path from :data:`dirPath`
        :rtype: str

        '''
        return self.dirPath

    def getFileName(self):
        '''
        Returns the file name of the video corresponding to this task.
        
        :return: file name from :data:`fileName`
        :rtype: str
        
        '''
        return self.fileName

    def setChanged(self, value):
        '''
        Sets :data:`changed` to the value in parameter.
        
        :param value: new value
        :type value: bool

        '''
        self.changed = value
        
    def getChanged(self):
        '''
        Return the current value of :data:`changed` 
        
        :return: value
        :rtype: bool

        '''
        return self.changed


if __name__ == '__main__':
    pt = PhenoTask(1, '/home/andrei/Videos/test/short.mkv')
    print(pt.getDirPath())
    print(pt.getFileName())
