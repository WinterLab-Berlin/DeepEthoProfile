#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 00:29:08 2021

@author: andrei
"""

from time import sleep, strftime
from datetime import datetime

class Logger:
    def __init__(self, logPath):
        self.setLogFile(logPath)

    def __del__(self):
        self.closeLogFile()

    def setLogFile(self, logPath):
        self.logFile = open(logPath, 'a')
        self.logFile.write(datetime.now().strftime("%y%m%d_%H%M%S"))
        self.logFile.write('opened processing log file')
        self.logFile.write('\n')

    def closeLogFile(self):
        self.logFile.close()

    def log(self, message, printMess=False):
        self.logFile.write(datetime.now().strftime("%y%m%d_%H%M%S"))
        self.logFile.write(' - ' + message)

        if printMess:
            print(message)


if __name__ == '__main__':
    logger = Logger('./test.log')
    logger.log('something')
