#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Andrei Istudor     andrei.istudor@gmail.com
"""

from threading import Lock

from PhenoTask import PhenoTask
from TaskState import TaskState

class TaskList:
    '''
    Class implementing a single access list for managing creation and accessing tasks.
    
    '''
    
    #: the list storing all the added tasks
    tasksList: []
    
    #: lock for accessing the :data:`tasksList`
    listLock: Lock
    
    def __init__(self):
        self.tasksList = []
        self.listLock = Lock()

    def addVideo(self, id, filename):
        '''
        Creates a new task with the provided parameters and adds it to the list.
        The list is locked during the process.
        
        :param id: the id of the new task
        :type id: int
        :param filename: the full path of the video file
        :type filename: str
        :return: the new task
        :rtype: PhenoTask

        '''
        with self.listLock:
            crtTask = PhenoTask(id, filename)
            self.tasksList.append(crtTask)
            return crtTask

    # def checkChanged(self):
    #     '''
    #     Checks if any of the tasks in :data:`tasksList` has changed
        
    #     :return: True if any of the added tasks changed, False otherwise
    #     :rtype: bool

    #     '''
    #     for i in range(len(self.tasksList)):
    #         crtTask = self.tasksList[i]
    #         if(crtTask.getChanged()):
    #             return True
    #     return False

    def getNewTask(self):
        '''
        Checks if there are any tasks with :data:`TaskState.TaskState.new` state in :data:`tasksList`. 
        If one is found, its status is changed to :data:`TaskState.TaskState.selected` and then it is returned.
        
        The access to the list is blocked during the execution.
        
        :return: selected task or None
        :rtype: PhenoTask

        '''
        with self.listLock:
            for i in range(len(self.tasksList)):
                crtTask = self.tasksList[i]
                if crtTask.state is TaskState.new:
                    crtTask.setState(TaskState.selected)
                    return crtTask

        #print('no waiting task found')
        return None



