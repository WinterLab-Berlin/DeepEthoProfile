#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Andrei Istudor
"""

import os
import sys

from PyQt5 import QtWidgets, QtMultimedia, uic, QtCore
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,
                             QAction, QFileDialog, QApplication)

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pathlib import Path

class add_task(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), "AddVideo.ui"), self)
        
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.ui.browseButton.clicked.connect(self.browseButtonClicked)
        self.ui.addBtn.clicked.connect(self.addButtonClicked)
    
    def browseButtonClicked(self):
        #print('browse')
        home_dir = str(Path.home())
        bfd = QFileDialog(self, 'Choose recording', home_dir + "/Videos/test/", "Videos(*.mkv)")
#        bfd.setFileMode(QFileDialog.ExistingFiles)

        if bfd.exec():
            filenames = bfd.selectedFiles()
#            print('selecte file(s): ', filenames)
            if(len(filenames) > 0):
                self.setVideoFile(filenames[0])
        #else:
          #  print('nothing selected')

    def addButtonClicked(self):
        #print('add')
        pass

    def setVideoFile(self, filename):
        self.ui.fileText.setText(filename)

        self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(filename)))
        self.player.setVideoOutput(self.ui.displayWidget)
        self.player.play()

        self.ui.addBtn.setEnabled(True)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = add_task()
    w.show()
    sys.exit(app.exec())
