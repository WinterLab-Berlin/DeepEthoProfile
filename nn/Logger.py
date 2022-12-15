#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger class

@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""

from time import sleep, strftime
from datetime import datetime

class Logger:
    '''
    Simple logger used mostly for debugging.
    '''
    
    #: handle to the file where the logs will be writtem
    logFile: str
    
    def __init__(self, logPath):
        self.setLogFile(logPath)

    def __del__(self):
        self.closeLogFile()

    def setLogFile(self, logPath):
        '''
        Creates :data:`logFile` handle to the 'logPath' location.
        
        :param logPath: path to where the log file will be created
        :type logPath: str

        '''
        self.logFile = open(logPath, 'a')
        self.logFile.write(datetime.now().strftime("%y%m%d_%H%M%S"))
        self.logFile.write('opened processing log file')
        self.logFile.write('\n')

    def log(self, message, printMess=False):
        '''
        Writes the `message` in through the file handle :data:`logFile`. 
        Every message will be preceeded by the current time.
        
        If `printMess` is true, the message will be also sent to the standard output.
        
        :param message: message to be logged
        :type message: str
        :param printMess: flag to print the message to the standard output, defaults to False
        :type printMess: bool, optional

        '''
        self.logFile.write(datetime.now().strftime("%y%m%d_%H%M%S"))
        self.logFile.write(' - ' + message)
        self.logFile.write('\n')
    
        if printMess:
            print(message)
            
    def closeLogFile(self):
        '''
        Closes the :data:`logFile` handle.

        '''
        self.logFile.close()



if __name__ == '__main__':
    logger = Logger('./test.log')
    logger.log('something')
