"""
pheno_ui - entry point 
@author: Andrei Istudor
"""

__version__ = 0.1

import os
import sys
import socket

from PyQt5 import QtWidgets, QtMultimedia, uic, QtCore
from queue import Queue

from add_task import add_task
from add_multiple import add_multiple
from TaskTableModel import TaskTableModel
from CentralCommand import CentralCommand
from TaskList import TaskList
from TaskState import TaskState

from PhenoPorts import guiPort

class pheno_ui(QtWidgets.QMainWindow):
"""
class definition - starts the User Interface
"""
    def __init__(self, nPreprocTasks = 2, nProcTasks = 1, parent=None):
        super(pheno_ui, self).__init__(parent)
#        self.newVideosQ = Queue()
        self.taskList = TaskList()
        self.nPreprocTasks = nPreprocTasks
        self.nProcTasks = nProcTasks

        self.startCommServer()

        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), "MainWindow.ui"), self)

        self.connectSignalsSlots()
        self.connectTableView()

        self.taskCounter = 0
        self.firstTask = True


    def connectSignalsSlots(self):
        self.actionQuit.triggered.connect(self.close)
        self.actionAdd_video.triggered.connect(self.addTaskClicked)
        self.actionAddMultiple.triggered.connect(self.addMultipleClicked)

    def connectTableView(self):
        self.tableData = [] #[[0, 'some long file name here for test', 0, 0]]
        self.tableModel = TaskTableModel(self.tableData)

        self.tableView = QtWidgets.QTableView()
        self.tableView.setModel(self.tableModel)
#        self.tableView.setColumnHidden(0, True)

 #       self.tableView.setColumnWidth(1, 610)
  #      self.tableView.setColumnWidth(2, 65)
   #     self.tableView.setColumnWidth(3, 65)

        self.listLayout.addWidget(self.tableView)

    def startCommServer(self):
        self.cc = CentralCommand(self.taskList)
        self.cc.start(self.nPreprocTasks, self.nProcTasks)

    def addMultipleClicked(self):
        self.addWindow = add_multiple()
        #        print('display dialog')
        if self.addWindow.exec():
            #           print('file add confirmed')
            videoList = self.addWindow.videoList
            print('video list arg: ', videoList)
            if(len(videoList) > 0):
                for f in videoList:
                    self.addNewFile(f)
        else:
            print('cancelled ')

    def addTaskClicked(self):
        self.addWindow = add_task()
#        print('display dialog')
        if self.addWindow.exec():
 #           print('file add confirmed')
            newFile = self.addWindow.ui.fileText.text()
            print('add new file: ', newFile)
            self.addNewFile(newFile)
        else:
            print('cancelled ')

    def addNewFile(self, file):
  #      print('added new file: ', file)
        self.taskCounter = self.taskCounter + 1

        newTask = self.taskList.addVideo(self.taskCounter, file)

        #connect to Task to update GUI
        newTask.progressQt.connect(self.updateProgress)
        newTask.stateQt.connect(self.updateState)

        self.tableData.append([self.taskCounter, file, 0, 0])
        self.tableModel.layoutChanged.emit()

        if self.firstTask:
            self.tableView.setColumnWidth(0, 15)
            self.tableView.setColumnWidth(1, 550)
            self.tableView.setColumnWidth(2, 70)
            self.tableView.setColumnWidth(3, 70)
            self.firstTask = False

#        lastIndex = len(self.tableData) - 1
#        print('last added video: ', self.tableData[lastIndex][0])

    def updateState(self, id, state):
#        print('task {} signal state={}'.format(id, state))
        #TODO: check state - finished?
        for crtEntry in self.tableData:
            if(crtEntry[0] == id):
                crtEntry[3] = state.name
                self.tableModel.layoutChanged.emit()

    def updateProgress(self, id, progress):
 #       print('task {} signal data={}'.format(id, progress))
        #TODO: check state - finished?
        for crtEntry in self.tableData:
            if(crtEntry[0] == id):
                crtEntry[2] = progress
                self.tableModel.layoutChanged.emit()

    def addNewTask(self, index, file):
        print('connect to server')

    def closeEvent(self, event):
        self.close()
        event.accept()

    def close(self):
        self.cc.stop()
        print('close call')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    nPreprocTasks = 2
    nProcTasks = 1
    #read from values from command line

    if len(sys.argv) > 1 and sys.argv[1].isdecimal():
        nPreprocTasks = int(sys.argv[1])
        if len(sys.argv) > 2 and sys.argv[2].isdecimal():
            nProcTasks = int(sys.argv[2])

    print('no Preproc tasks = {}'.format(nPreprocTasks))
    print('no Processing tasks = {}'.format(nProcTasks))

    w = pheno_ui(nPreprocTasks, nProcTasks)
    w.show()

    #TODO: close thread
    sys.exit(app.exec())
