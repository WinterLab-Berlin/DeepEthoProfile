"""
Entry point
    - creates the UI and its connections
    - starts the CentralCommand background thread that manages the processing instances

@author: Andrei Istudor     andrei.istudor@hu-berlin.de
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

class pheno_ui(QtWidgets.QMainWindow):
    '''
    The pheno_ui loads the graphic definition from *MainWindow.ui* and exposes the functionality to the user.

    Takes one optional parameter, the maximum number of Docker processing instances - default is 1
    '''
    def __init__(self, nProcTasks = 1, parent=None):
        super(pheno_ui, self).__init__(parent)

        self.taskList = TaskList()
        self.nProcTasks = nProcTasks

        self.startCommServer()

        self.ui = uic.loadUi(os.path.join(os.path.dirname(__file__), "MainWindow.ui"), self)

        self.connectSignalsSlots()
        self.connectTableView()

        self.taskCounter = 0
        self.firstTask = True

    #: Maximum number of processing tasks that will be running in parallel
    nProcTasks: int

    #: Contains all the added files
    taskList: TaskList

    #: Contains the view of data as it is displayed in the table of the main window
    tableData: []

    #: The background object handling the execution of the annotation processes and
    #: the related communication between them and the user interface
    cc: CentralCommand
    taskCounter: int
    firstTask: bool
    

    def connectSignalsSlots(self):
        """
        Establishes communication between :class:`pheno_ui` and the GUI signals.
        """
        self.actionQuit.triggered.connect(self.close)
        self.actionAdd_video.triggered.connect(self.addTaskClicked)
        self.actionAddMultiple.triggered.connect(self.addMultipleClicked)

    def connectTableView(self):
        """
        Connects the *tableData* to the main window. 
        This data will be displayed in a table according to the specification 
        from :class:`TaskTableModel.TaskTableModel`
        """
        self.tableData = [] #[[0, 'some long file name here for test', 0, 0]]
        self.tableModel = TaskTableModel(self.tableData)

        self.tableView = QtWidgets.QTableView()
        self.tableView.setModel(self.tableModel)

        self.listLayout.addWidget(self.tableView)

    def addMultipleClicked(self):
        '''
        Opens the :class:`add_multiple.add_multiple` dialog that allows to select and add several video files at once
        '''
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
        '''
        Opens the :class:`add_task.add_task` dialog that allows to select, view, and add one video file to be processed
        '''
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
        '''
        Adds new file to taskList and sets the appropiate events
        '''

        self.taskCounter = self.taskCounter + 1

        newTask = self.taskList.addVideo(self.taskCounter, file)

        #connect to Task to update GUI
        newTask.progressQt.connect(self.updateProgress)
        newTask.stateQt.connect(self.updateState)

        self.tableData.append([self.taskCounter, file, 'queued', 'new'])
        self.tableModel.layoutChanged.emit()

        if self.firstTask:
            self.tableView.setColumnWidth(0, 15)
            self.tableView.setColumnWidth(1, 550)
            self.tableView.setColumnWidth(2, 70)
            self.tableView.setColumnWidth(3, 90)
            self.firstTask = False

#        lastIndex = len(self.tableData) - 1
#        print('last added video: ', self.tableData[lastIndex][0])

    def updateState(self, id, state):
        '''
        Updates the displayed state of a task        

        :param id: The id of the element to be updated
        :type id: int
        :param state: The new state
        :type state: :class:`TaskState.TaskState`

        '''

        for crtEntry in self.tableData:
            if(crtEntry[0] == id):
                crtEntry[3] = state.name
                self.tableModel.layoutChanged.emit()

    def updateProgress(self, id, progress):
        '''
        Updates the displayed execution progress of a task        

        :param id: The id of the element to be updated
        :type id: int
        :param progress: The new progress percentage
        :type progress: float
        
        '''
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

    
    def startCommServer(self):
        '''
        Construct a :class:`CentralCommand.CentralCommand` object in :data:`cc` and start it in the background.

        '''
        self.cc = CentralCommand(self.taskList)
        self.cc.start(self.nProcTasks)
    


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    #default using just one Docker instance for processing
    nProcTasks = 1
    
    #read from values from command line
    if len(sys.argv) > 1 and sys.argv[1].isdecimal():
        if len(sys.argv) > 2 and sys.argv[2].isdecimal():
            nProcTasks = int(sys.argv[2])

    print('no Processing tasks = {}'.format(nProcTasks))

    w = pheno_ui(nProcTasks)
    w.show()

    #TODO: close thread
    sys.exit(app.exec())
