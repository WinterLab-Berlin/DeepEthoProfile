"""
Basic interface between the UI and the processing module

@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""


import socket
from sys import argv
from os import path
import time

import subprocess

# from main import processVideo
from ProcessVideo import ProcessVideo
from Logger import Logger

# def setNonBlocking(fd):
#     flags = fcntl.fcntl(fd, fcntl.F_GETFL)
#     flags = flags | os.O_NONBLOCK
#     fcntl.fcntl(fd, fcntl.F_SETFL, flags)

class ProcComm:
    def __init__(self, port = 2000):
        self.port = port
        self.connSocket = None

    def start_sockServer(self):
        print('start')
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        serverSocket.bind(('0.0.0.0', self.port))  # 0.0.0.0
        serverSocket.listen(1)
        (self.connSocket, address) = serverSocket.accept()

        helloMessage = 'Here is Processing Docker instance'
        self.sendMessage(helloMessage)
        time.sleep(1)

        print('sent message: ', helloMessage)

        fileName = self.receiveMessage()

        if(fileName is not None):
            mountDir='/mnt/data'
            # localDir = '/home/nn'
            # videoFilePath = path.join(mountDir, fileName)
            # inputVideo = ''
            inputVideo = path.join(mountDir, fileName)
            logPath = ''
            outputFile = ''

            if(fileName.endswith('mkv')):
                # inputVideo = fileName #.replace('.mkv', '.avi')
                logPath = inputVideo.replace('.mkv', '_nn.log')
                outputFile = inputVideo.replace('.mkv', '_results_v3.csv')
            elif(fileName.endswith('avi')):
                # inputVideo = fileName#.replace('.avi', '_c.avi')
                logPath = inputVideo.replace('.avi', '_nn.log')
                outputFile = inputVideo.replace('.avi', '_results_v3.csv')
            else:
                self.sendMessage('invalid video file {}'.format(fileName))
                serverSocket.close()
                return

            
            logger = Logger(logPath)

            self.sendMessage('processing file {}'.format(inputVideo))
            self.callProc(inputVideo, outputFile, logger)
        else:
            self.sendMessage('file name is not valid')


    def sendMessage(self, message):
        message = message.encode('ascii')
        msgSize = str(len(message))

        sent = self.connSocket.send(msgSize.encode('ascii'))
        if sent == 0:
            raise RuntimeError("socket connection broken")

        sent = self.connSocket.send(message)
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def receiveMessage(self):
        msgSize = self.connSocket.recv(2)

        if msgSize == b'' or len(msgSize) == 0:
            print('could not read size, exiting')
        else:
            size = int(msgSize.decode('ascii'))
            #print('msg size = ', size)

            message = self.connSocket.recv(size)
            if len(message) == size:
                print('msg  = ', message)
                return message.decode('ascii')
            else:
                print('did not read complete message, exiting: ', message)

        return None

    def callProc(self, videoFile, outputFile, logger):
        progress = 0
        
        logger.log('process video {} with output {} \n'.format(videoFile, outputFile))
        proc = ProcessVideo('./mouse_v2.model', 10, videoFile, outputFile)
        
        try:
            crtStep = 0
            for x in proc.process(logger):
                crtStep = crtStep + 1
                # logger.log('processing step')

                if(crtStep % 20 == 0):
                    mess = 'processing percent: {} \n'.format(x)
                    self.sendMessage(mess)
                    # logger.log(mess)
                    
        except StopIteration:
            logger.log('finished at step {} \n'.format(crtStep))
            pass



if __name__ == '__main__':
#    print('argv: ', argv[1])
 #   file = argv[1]
#    port = 2000
    pc = ProcComm()
    #cb.callPreProc('short.mkv', '/home/andrei/Videos/test')
    pc.start_sockServer()
    # pc.callProc(file)


#"/home/andrei/Documents/background/preprocess/bin/preprocess"

#$PROCESS --computeBG 01_20180815_0000.mkv --bgFrames 50
