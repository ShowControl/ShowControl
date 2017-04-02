# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SelectNew.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SelectNew(object):
    def setupUi(self, SelectNew):
        SelectNew.setObjectName("SelectNew")
        SelectNew.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(SelectNew)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.comboBox_SelectNew = QtWidgets.QComboBox(SelectNew)
        self.comboBox_SelectNew.setToolTip("")
        self.comboBox_SelectNew.setObjectName("comboBox_SelectNew")
        self.gridLayout.addWidget(self.comboBox_SelectNew, 1, 0, 1, 1)
        self.label_SelectNew = QtWidgets.QLabel(SelectNew)
        self.label_SelectNew.setObjectName("label_SelectNew")
        self.gridLayout.addWidget(self.label_SelectNew, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(SelectNew)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SelectNew)
        self.buttonBox.accepted.connect(SelectNew.accept)
        self.buttonBox.rejected.connect(SelectNew.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectNew)

    def retranslateUi(self, SelectNew):
        _translate = QtCore.QCoreApplication.translate
        SelectNew.setWindowTitle(_translate("SelectNew", "Select New"))
        self.label_SelectNew.setText(_translate("SelectNew", "TextLabel"))

