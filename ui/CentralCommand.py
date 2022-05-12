#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Andrei Istudor
"""

import os.path
import queue
import socket
import time
from threading import Thread, Lock
import docker
import subprocess

from os import path

from PhenoPorts import *
from ProcessingComm import ProcessingComm
from PortPool import PortPool
from TaskState import TaskState
from PhenoTask import PhenoTask

class CentralCommand:
    def __init__(self, taskList):
        print('init CentralCommand')
        self.taskList = taskList
#        self.guiFiles = Queue()

        self.started = True

    def start(self, noPreProcClients = 2, noProcClients = 2):
        print('nPre = {}, nProc = {}'.format(noPreProcClients, noProcClients))
        self.procPortPool = PortPool(noProcClients)

        self.guiConnThread = Thread(target=self.startGUIConnection)
        self.guiConnThread.start()

    def stop(self):
        self.started = False
        #TODO: propagate stop to processes/Docker

    def receiveMessage(self, connSocket):
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
        aMessage = message.encode('ascii')
        msgSize = str(len(aMessage))

        sent = connSocket.send(msgSize.encode('ascii'))
        if sent == 0:
            raise RuntimeError("socket connection broken")

        sent = connSocket.send(aMessage)
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def startProc(self, port, task):
        taskDir = task.getDirPath()

        crtPort = procPort + port
        print('start processing NN docker image on port: ', crtPort)

        client = docker.from_env()
        client.containers.run("ethoprofiler_nn", detach=True, ports={2000: crtPort},
                              device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])],        #runtime="nvidia",
                              volumes={taskDir: {'bind': '/mnt/data', 'mode': 'rw'}})

        # TODO: check if docker image is up?
        time.sleep(5)

        self.procThread = Thread(target=self.procVideo, args=(port, task,))
        self.procThread.start()

        # self.computeBg(crtPort, task)

    def procVideo(self, port, task):
        crtPort = procPort + port
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

        task.setProgress(0)
        task.setState(TaskState.proc)

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
                            task.setProgress(x)
                    else:
                        print(feedBack)
                else:
                    print(feedBack)

        task.setProgress(100)
        task.setState(TaskState.finished)

        # wait for docker to close
        time.sleep(5)

        self.procPortPool.resetPort(port)

    def stop(self):
        self.started = False

    def startGUIConnection(self):
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

if __name__ == '__main__':
    cc = CentralCommand(None)

    tTask = PhenoTask(0, '/home/andrei/Videos/test/04_20180815_1200.mkv')
#    tTask = PhenoTask(0, '/home/andrei/Videos/test/06_20180419_0000.mkv')
    cc.computeBg(0, tTask)
