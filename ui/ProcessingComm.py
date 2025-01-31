#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Andrei Istudor     andrei.istudor@gmail.com
"""

from threading import Thread, Lock
import socket

class ProcessingComm:
    def __init__(self, id, port, state=0):
        self.id = id
        self.state = state
        self.sockPort = port
        self.filename = ''
        self.socket = 0

    def startComm(self):
        print('create communication socket on port ', self.sockPort)

        self.procSocket.listen(1)

        (clientSocket, address) = self.procSocket.accept()


    def createCommSocket(self, clientSocket):
        self.procSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.procSocket.bind(('localhost', self.sockPort))

        #start dedicated communication thread for this processing server
        self.sProcThread = Thread(target=self.startComm)
        self.sProcThread.start()

        #send the port to be used
        message = str(self.sockPort).encode('ascii')
        msgSize = str(len(message))

        sent = clientSocket.send(msgSize.encode('ascii'))
        if sent == 0:
            raise RuntimeError("socket connection broken")

        sent = clientSocket.send(message)
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def getStatus(self):
        print('return current status')
        return self.state

    def addFile(self, file):
        if self.state == 0:
            print('add file to process')
            return 0
        else:
            print('cannot process file, process is busy')
            return -1

