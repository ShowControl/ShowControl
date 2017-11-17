import sys

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class FileFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FileFilterProxyModel, self).__init__(parent)

    def filterAcceptsRow(self, source_row, srcidx):
        model = self.sourceModel()
        index0 = model.index(source_row, 0, srcidx)
        index1 = model.index(source_row, 1, srcidx)
        index2 = model.index(source_row, 2, srcidx)
        str0_filenamerole = model.data(index0, QFileSystemModel.FileNameRole)
        str0_displayrole = model.data(index0, Qt.DisplayRole)
        fname = model.fileName(index0)
        fname1 = model.fileName(index1)
        str1_filenamerole = model.data(index1, QFileSystemModel.FileNameRole)
        str1_displayrole = model.data(index1, Qt.DisplayRole)
        str2_filenamerole = model.data(index2, QFileSystemModel.FileNameRole)
        str2_displayrole = model.data(index2, Qt.DisplayRole)
        print('source_rowe: {}'.format(source_row))
        print('str0_filenamerole: {}'.format(str0_filenamerole))
        print('str0_displayrole: {}'.format(str0_displayrole))
        print('str1_filenamerole: {}'.format(str1_filenamerole))
        print('str1_displayrole: {}'.format(str1_displayrole))
        print('str2_filenamerole: {}'.format(str2_filenamerole))
        print('str2_displayrole: ~{}~'.format(str2_displayrole))
        if str2_displayrole in ('Folder', 'Drive'): return True
        if '_project' in str1_filenamerole and str2_displayrole == 'xml File':
            print('Returning True')
            return True
        else:
            return False

app = QtWidgets.QApplication(sys.argv)
dlg = QFileDialog()
proxymodel = FileFilterProxyModel(dlg)
dlg.setDirectory('/home/mac/Shows/Fiddler/')
dlg.setProxyModel(proxymodel)
dlg.show()
app.exec_()