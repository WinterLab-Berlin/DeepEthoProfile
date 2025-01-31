#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Andrei Istudor     andrei.istudor@gmail.com
"""

import os
import sys

from PyQt5 import QtWidgets, QtMultimedia, uic, QtCore
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,
                             QAction, QFileDialog, QApplication)

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pathlib import Path


class add_multiple(QtWidgets.QDialog):
    """
    Dialog allowing the selection and adding of multiple videos from one folder at once.
    
    The visual representation is specified in *AddMultiple.ui* file.

    """
    
    #: Array of paths to selected video files. The :class:`pheno_ui.pheno_ui` instance will check this array for new videos to be added in the processing queue.
    videoList: []
    
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), "AddMultiple.ui"), self)

        self.videoList = []
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        '''
        Establishes communication between :class:`add_multiple` and the GUI signals.
        '''
        self.ui.selectVideosButton.clicked.connect(self.browseButtonClicked)

    def browseButtonClicked(self):
        '''
        Opens the selection dialog `QFileDialog`
        
        In the case of successful selection, the paths to the videos will be stored in :data:`videoList`.
        '''
        # print('browse')
        home_dir = str(Path.home())
        bfd = QFileDialog(self, 'Choose recording', home_dir + "/Videos/", "Videos(*.mkv)")
        bfd.setFileMode(QFileDialog.ExistingFiles)

        if bfd.exec():
            filenames = bfd.selectedFiles()
            print('selecte file(s): ', filenames)
            if (len(filenames) > 0):
                print('add files to list')
                for f in filenames:
                    self.videoList.append(f)
                model = QStringListModel(self.videoList)
                self.ui.listView.setModel(model)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = add_multiple()
    w.show()
    sys.exit(app.exec())
