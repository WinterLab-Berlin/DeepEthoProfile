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
    '''
    Provides a basic interface for creating and communicating with the :class:`ProcessVideo.ProcessVideo` class. 
    
    This is the entry point of the Docker instance. 
    '''
    
    #: port on which the connection will be established, default is 2000
    port: int
    
    #: connection socket to send and receive data
    connSocket: socket.socket
    
    def __init__(self, port = 2000):
        self.port = port
        self.connSocket = None

    def start_sockServer(self):
        '''
        Creates a socket listening on the :data:`port` port. 
        When running inside a Docker instance, this port is internal, 
        and the mapping to the local system communication port is done at creation time.
        
        When the connection is established, the method reads the file name 
        that is to be processed and creates the file name for the output. 
        The full file names are relative to the Docker instance mounted folder.
        
        It then starts the processing by calling :func:`callProc`

        '''
        print('start')
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        serverSocket.bind(('0.0.0.0', self.port))  # 0.0.0.0
        serverSocket.listen(1)
        (self.connSocket, address) = serverSocket.accept()

        helloMessage = 'Here is Processing Docker instance'
        try:
            self.sendMessage(helloMessage)
        except RuntimeError:
            print('error sending first message')
            serverSocket.close()
            return
            
        time.sleep(1)

        print('sent message: ', helloMessage)

        fileName = self.receiveMessage()

        if(fileName is not None):
            mountDir='/mnt/data'
            # localDir = '/home/nn'
            # videoFilePath = path.join(mountDir, fileName)
            # inputVideo = ''
            inputVideo = path.join(mountDir, fileName)
            logPath = inputVideo + '.log'
            outputFile = ''

            #creates a logger that will be used by the processing
            logger = Logger(logPath)
            logger.log('init logger for video ' + inputVideo)

            if(fileName.endswith('mkv')):
                # inputVideo = fileName #.replace('.mkv', '.avi')
                outputFile = inputVideo.replace('.mkv', '_results_v5.csv')
                logger.log('output file is ' + outputFile)
            elif(fileName.endswith('avi')):
                # inputVideo = fileName#.replace('.avi', '_c.avi')
                outputFile = inputVideo.replace('.avi', '_results_v5.csv')
                logger.log('output file is ' + outputFile)
            else:
                try:
                    self.sendMessage('invalid video file {}'.format(fileName))
                    logger.log('invalid video file {}'.format(fileName))
                except RuntimeError:
                    print('error sending message')
                    
                serverSocket.close()
                
                return

            try:
                self.sendMessage('processing file {}'.format(inputVideo))
                self.callProc(inputVideo, outputFile, logger)
            except RuntimeError:
                logger.log('error sending confirmation')
        else:
            self.sendMessage('file name is not valid')

    def callProc(self, videoFile, outputFile, logger):
        '''
        Creates an instance of :class:`ProcessVideo.ProcessVideo` for and calls the :func:`ProcessVideo.ProcessVideo.process`
        method until the whole video is processed. It regularily sends the progress feed-back
        through the :data:`connSocket` socket. 
        
        :param videoFile: full path to the video file to be processed
        :type videoFile: str
        :param outputFile: full path to the output file
        :type outputFile: str
        :param logger: simple logger used mostly for debugging
        :type logger: Logger.Logger

        '''

        logger.log('= process video {} with output {} \n'.format(videoFile, outputFile))
        proc = ProcessVideo('./mouse_v5.model', 8, videoFile, outputFile)
        
        try:
            crtStep = 0
            for x in proc.process(logger):
                crtStep = crtStep + 1
                # logger.log('! processing step', crtStep)
    
                if(crtStep % 20 == 0):
                    logger.log('@ processing percent: {} \n'.format(x))
                    mess = 'processing percent: {} \n'.format(x)
                    try:
                        self.sendMessage(mess)
                        # logger.log(mess)
                    except RuntimeError:
                        break
                    
        except StopIteration:
            logger.log('finished at step {} \n'.format(crtStep))
            pass
    

    def sendMessage(self, message):
        '''
        Sends the size of the `message` and the contents through the :data:`connSocket` socket
        
        :param message: data to be sent
        :type message: str
        :raises RuntimeError: raised when socket send method fails

        '''
        message = message.encode('ascii')
        msgSize = str(len(message))

        sent = self.connSocket.send(msgSize.encode('ascii'))
        if sent == 0:
            raise RuntimeError("socket connection broken")

        sent = self.connSocket.send(message)
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def receiveMessage(self):
        '''
        Reads a message from the :data:`connSocket` socket
        
        :return: message data that was read
        :rtype: str

        '''
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



if __name__ == '__main__':
#    print('argv: ', argv[1])
 #   file = argv[1]
#    port = 2000
    pc = ProcComm()
    pc.start_sockServer()
    # pc.callProc(file)



#$PROCESS --computeBG 01_20180815_0000.mkv --bgFrames 50
