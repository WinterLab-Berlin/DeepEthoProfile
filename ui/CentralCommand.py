#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""

import os.path
import queue
import socket
import time
from threading import Thread, Lock
import docker
import subprocess

from os import path

# from PhenoPorts import *
# from ProcessingComm import ProcessingComm
from PortPool import PortPool
from TaskState import TaskState
from PhenoTask import PhenoTask
from TaskList import TaskList

class CentralCommand:
    '''
    Processes the videos added by the user through :data:`taskList`. This list is updated every time a new video is added or the status of any of the containing tasks is changed.
    
    Provides the communication between the Docker instance(s) and the user interface.
    '''

    #: Contains the list of all the video files that were added by the user. Is passed as parameter when instantiating the class.
    taskList: TaskList

    #: A list of ports currently available for opening communication channels to Docker images.
    procPortPool: PortPool
    
    #: An offset for computing the communication ports between the Docker instances and the main application
    procPort = 20100
    
    started: bool
    #: Flag that controls the processing of new tasks. Initialied to False in the constructor.
    
    guiConnThread: Thread
    #: Thread that takes new tasks from :data:`taskList` and prepares them for execution.

    def __init__(self, taskList):
        print('init CentralCommand')
        self.taskList = taskList

        self.started = False

    def start(self, noProcClients = 2):
        '''
        Starts the method :func:`startGUIConnection` in a thread. This will process the videos that are added in the :data:`taskList`.
        
        Initializes the :class:`PortPool` with the appropiate number of processes.
        
        :param noProcClients: maximum number of tasks that will be processed in parallel, defaults to 2
        :type noProcClients: int, optional

        '''
        
        if(self.started == False):
            self.started = True
            
            print('nProc = {}'.format(noProcClients))
            self.procPortPool = PortPool(noProcClients)
    
            self.guiConnThread = Thread(target=self.startGUIConnection)
            self.guiConnThread.start()
        else:
            print('CC.startGUIConnection already running ')

    def stop(self):
        '''
        Informs the :func:`startGUIConnection` to stop processing new tasks.
        
        The processing of videos in Docker images that are already started will run until they are finished and produce valid, complete results.

        '''
        self.started = False
        #TODO: propagate stop to processes/Docker

    def startGUIConnection(self):
        '''
        Runs a loop as long as the flag :data:`started` is True. The method is started in a thread by :func:`start`.
        
        It checks for available communication ports in :data:`procPortPool` and tasks waiting to be executed in :data:`taskList`. 
        When it has found both, it starts a new process by calling the method :func:`startProc`.

        '''
        while self.started:
            freeProcPort = self.procPortPool.getPort()
            if freeProcPort >= 0:
                #print('start new processing task?')
                procTask = self.taskList.getNewTask()
                if procTask is not None:
                    print('add new processing task to proc pool')
                    self.startProc(freeProcPort, procTask)
                else:
                    self.procPortPool.resetPort(freeProcPort)
                    #print('--no processing in queue')
                    time.sleep(10)


    def startProc(self, port, task):
        '''
        Prepares the environment for the processing of a new video.
        A new Docker instance is created from the image *ethoprofiler_nn_av*. 
        This image mounts the directory where the video file is found locally at */mnt/data*. 
        There is also a mapping between the Docked instance internal port 2000 and the communication port used to connect to the main application.
        
        After the Docker instance is created, a new thread running :func:`procVideo` is started to handle the communication with it.
        
        :param port: needed to compute the port where the communication between the main application and the Docker instance will happen
        :type port: int
        :param task: PhenoTask object containing the path to the video that will be processed
        :type task: PhenoTask

        '''
        taskDir = task.getDirPath()

        crtPort = self.procPort + port
        print('start processing NN docker image on port: ', crtPort)

        client = docker.from_env()
        client.containers.run("ethoprofiler_nn_av", detach=True, ports={2000: crtPort}, remove=True,
                              device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])],        #runtime="nvidia",
                              volumes={taskDir: {'bind': '/mnt/data', 'mode': 'rw'}})

        # TODO: check if docker image is up?
        time.sleep(5)

        self.procThread = Thread(target=self.procVideo, args=(port, task,))
        self.procThread.start()

        # self.computeBg(crtPort, task)

    def procVideo(self, port, task):
        '''
        Provides an interface with a Docker instance. 
        The communication is performed through a port identified in parameter and the video file to be processed is contained in task.
        
        It updates the ``task`` with the current execution status - this will be propagated to the user interface.
        
        :param port: offset of the communication port with the Docker instance
        :type port: int
        :param task: contains the video file name and state signals
        :type task: PhenoTask

        '''
        crtPort = self.procPort + port
        print('start processing video for file {} on port {}'.format(task.getFileName(), crtPort))

        connSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSocket.connect(('localhost', crtPort))

        dockerInitMess = self.receiveMessage(connSocket)
        if (dockerInitMess == ''):
            print('error initializing comm for processing task {} on port {}'.format(task.id, crtPort))
            return None

        print('processing docker says: ', dockerInitMess)
        time.sleep(1)

        try:
            self.sendMessage(connSocket, task.getFileName())
        except:
            print('error sending file for bg for task {} on port {}'.format(task.id, crtPort))
            return None

        time.sleep(5)

        confirmMess = self.receiveMessage(connSocket)
        if (confirmMess == ''):
            print('error acknowledge comm for task {} on port {}'.format(task.id, crtPort))
            return None
        print('processing docker says: ', confirmMess)

        #mark the processing of the video as started
        task.setProgress(0)
        task.setState(TaskState.processing)

        #crtProg = 1
        while True:
            feedBack = self.receiveMessage(connSocket)
            if (feedBack == ''):
                print('finished processing video')
                break
            else:
                m = feedBack.split(':')
                x = 0
                if len(m) > 1:
                    xm = m[1].strip()
                    if(xm.isdecimal()):
                        x = int(xm)
                        #print('processing video id {} on port {}: progress= {}'.format(str(task.id), str(port), x))
                        #crtProg = crtProg + 1
                        if x < 100:
                            #update progress
                            task.setProgress(x)
                    else:
                        print(feedBack)
                else:
                    print(feedBack)

        #mark the processing as finished
        task.setProgress(100)
        task.setState(TaskState.finished)

        # wait for docker to close
        time.sleep(5)

        self.procPortPool.resetPort(port)

    def receiveMessage(self, connSocket):
        '''
        Receives a message from a Docker instance through the socket ``connSocket``, decodes it and returns the string version.
        
        :param connSocket: communication socket where the message is to be received
        :type connSocket: socket.socket
        :return: decoded version of the received message or ''
        :rtype: str

        '''
        
        msgSize = connSocket.recv(2)
    
        if msgSize == b'' or len(msgSize) == 0:
            print('could not read size, exiting')
        else:
            size = int(msgSize.decode('ascii'))
            #print('msg size = ', size)
    
            message = connSocket.recv(size)
            if len(message) == size:
                return message.decode('ascii')
            else:
                print('did not read complete message, exiting: ', message)
    
        return ''
    
    def sendMessage(self, connSocket, message):
        '''
        Encodes the ``message`` and sends it through the ``connSocket``
        
        :param connSocket: socket through which to send the message
        :type connSocket: connSocket: socket.socket
        :param message: message to be sent
        :type message: str
        :raises RuntimeError: in case of failed send

        '''
        aMessage = message.encode('ascii')
        msgSize = str(len(aMessage))
    
        sent = connSocket.send(msgSize.encode('ascii'))
        if sent == 0:
            raise RuntimeError("socket connection broken")
    
        sent = connSocket.send(aMessage)
        if sent == 0:
            raise RuntimeError("socket connection broken")


if __name__ == '__main__':
    cc = CentralCommand(None)

    tTask = PhenoTask(0, '/home/andrei/Videos/test/04_20180815_1200.mkv')
#    tTask = PhenoTask(0, '/home/andrei/Videos/test/06_20180419_0000.mkv')
    cc.computeBg(0, tTask)
