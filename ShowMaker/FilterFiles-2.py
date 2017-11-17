import sys

from PyQt5 import Qt, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class FileFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FileFilterProxyModel, self).__init__(parent)

    def filterAcceptsRow(self, source_row, srcidx):
        model = self.sourceModel()
        index0 = model.index(source_row, 0, srcidx)
        index2 = model.index(source_row, 2, srcidx)
        str0_filenamerole = model.data(index0, QFileSystemModel.FileNameRole)
        str2_displayrole = model.data(index2, Qt.DisplayRole)
        indexofstring = self.filterRegExp().indexIn(str0_filenamerole)
        if (indexofstring >= 0 and str2_displayrole == 'xml File')\
                or (str2_displayrole in ('Folder', 'Drive')):
            return True
        else:
            return False

app = QtWidgets.QApplication(sys.argv)
dlg = QFileDialog()
proxymodel = FileFilterProxyModel(dlg)
proxymodel.setFilterRegExp(QRegExp("_project", Qt.CaseInsensitive, QRegExp.FixedString))
dlg.setDirectory('/home/mac/Shows/Fiddler/')
dlg.setProxyModel(proxymodel)
dlg.show()
app.exec_()