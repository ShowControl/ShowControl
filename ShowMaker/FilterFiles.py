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
        index0 = model.index(source_row, 0, QtCore.QModelIndex())
        index1 = model.index(source_row, 1, QtCore.QModelIndex())
        index2 = model.index(source_row, 2, QtCore.QModelIndex())
        index3 = model.index(source_row, 3, QtCore.QModelIndex())
        index4 = model.index(source_row, 4, QtCore.QModelIndex())
        str0 = model.data(index0, Qt.DisplayRole)
        str1 = model.data(index1, Qt.DisplayRole)
        str2 = model.data(index2, Qt.DisplayRole)
        str3 = model.data(index3, Qt.DisplayRole)
        str4 = model.data(index4, Qt.DisplayRole)
        print('{}, data: {}{}{}'.format(source_row, str0, str1, str2))
        return True

app = QtWidgets.QApplication(sys.argv)
dlg = QFileDialog()
proxymodel = FileFilterProxyModel(dlg)
dlg.setProxyModel(proxymodel)
dlg.setDirectory('/home/mac/BasicQtSort/')
#dlg.setOption(QFileDialog.DontUseNativeDialog)
dlg.show()
sys.exit(app.exec_())