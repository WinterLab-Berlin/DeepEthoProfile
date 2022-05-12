#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: andrei
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
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), "AddMultiple.ui"), self)

        self.videoList = []
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.ui.selectVideosButton.clicked.connect(self.browseButtonClicked)
        #self.ui.addBtn.clicked.connect(self.addButtonClicked)

    def browseButtonClicked(self):
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

    def addButtonClicked(self):
        # print('add')
        pass

    def setVideoFile(self, filename):
        self.ui.fileText.setText(filename)

        self.ui.addBtn.setEnabled(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = add_multiple()
    w.show()
    sys.exit(app.exec())