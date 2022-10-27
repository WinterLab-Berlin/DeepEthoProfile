#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Andrei Istudor
"""

from threading import Lock

from PhenoTask import PhenoTask
from TaskState import TaskState

class TaskList:
    def __init__(self):
        self.tasksList = []
        self.listLock = Lock()

    def addVideo(self, id, filename):
        with self.listLock:
            crtTask = PhenoTask(id, filename)
            self.tasksList.append(crtTask)
            return crtTask

    def checkChanged(self):
        for i in range(len(self.tasksList)):
            crtTask = self.tasksList[i]
            if(crtTask.getChanged()):
                return True
        return False

    def getNewTask(self):
        with self.listLock:
            for i in range(len(self.tasksList)):
                crtTask = self.tasksList[i]
                if crtTask.state is TaskState.new:
                    crtTask.setState(TaskState.selected)
                    return crtTask

        #print('no waiting task found')
        return None



