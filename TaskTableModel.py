#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Andrei Istudor
"""

import sys
from PyQt5.QtCore import QModelIndex, Qt, QAbstractTableModel
from PyQt5 import QtWidgets

class TaskTableModel(QAbstractTableModel):
    def __init__(self, data=[[]], parent=None):
        super().__init__(parent)
        self.data = data

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Id"
                if section == 1:
                    return "File"
                elif section == 2:
                    return "Status"
                elif section == 3:
                    return "Progress"
            else:
                return "Task " + str(section)

    def columnCount(self, parent=None):
        if(len(self.data) > 0):
            return len(self.data[0])
        return 0

    def rowCount(self, parent=None):
        return len(self.data)

    def data(self, index: QModelIndex, role: int):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()

            return str(self.data[row][col])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    data = [[0, 1, 12, 13],
            [0, 2, 22, 23],
            [0, 3, 312, 13],
            [0, 4, 422, 23],
            [0, 5, 512, 13],
            [0, 6, 622, 23],
            [0, 7, 732, 33]]

    model = TaskTableModel(data)
    view = QtWidgets.QTableView()
    view.setModel(model)
    view.setColumnHidden(0, True)

    view.show()

    data.append([0, 1, 1, 1])
    view.model().layoutChanged.emit()

    sys.exit(app.exec_())