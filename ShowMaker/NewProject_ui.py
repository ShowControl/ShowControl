# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NewProject.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog_newproject(object):
    def setupUi(self, Dialog_newproject):
        Dialog_newproject.setObjectName("Dialog_newproject")
        Dialog_newproject.resize(786, 310)
        self.gridLayout = QtWidgets.QGridLayout(Dialog_newproject)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_newproject)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_projectfolder = QtWidgets.QLineEdit(Dialog_newproject)
        self.lineEdit_projectfolder.setObjectName("lineEdit_projectfolder")
        self.horizontalLayout.addWidget(self.lineEdit_projectfolder)
        self.pushButtonselectfolder = QtWidgets.QPushButton(Dialog_newproject)
        self.pushButtonselectfolder.setMaximumSize(QtCore.QSize(27, 16777215))
        self.pushButtonselectfolder.setObjectName("pushButtonselectfolder")
        self.horizontalLayout.addWidget(self.pushButtonselectfolder)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 3, 0, 1, 1)
        self.label_projectfolder = QtWidgets.QLabel(Dialog_newproject)
        self.label_projectfolder.setMaximumSize(QtCore.QSize(16777215, 28))
        self.label_projectfolder.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_projectfolder.setObjectName("label_projectfolder")
        self.gridLayout_2.addWidget(self.label_projectfolder, 1, 0, 1, 1)
        self.lineEdit_projectname = QtWidgets.QLineEdit(Dialog_newproject)
        self.lineEdit_projectname.setObjectName("lineEdit_projectname")
        self.gridLayout_2.addWidget(self.lineEdit_projectname, 0, 1, 1, 1)
        self.label_projectname = QtWidgets.QLabel(Dialog_newproject)
        self.label_projectname.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_projectname.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_projectname.setObjectName("label_projectname")
        self.gridLayout_2.addWidget(self.label_projectname, 0, 0, 1, 1)
        self.label_cuefile = QtWidgets.QLabel(Dialog_newproject)
        self.label_cuefile.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_cuefile.setObjectName("label_cuefile")
        self.gridLayout_2.addWidget(self.label_cuefile, 2, 0, 1, 1)
        self.lineEdit_projectcuefile = QtWidgets.QLineEdit(Dialog_newproject)
        self.lineEdit_projectcuefile.setObjectName("lineEdit_projectcuefile")
        self.gridLayout_2.addWidget(self.lineEdit_projectcuefile, 2, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)

        self.retranslateUi(Dialog_newproject)
        self.buttonBox.accepted.connect(Dialog_newproject.accept)
        self.buttonBox.rejected.connect(Dialog_newproject.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_newproject)

    def retranslateUi(self, Dialog_newproject):
        _translate = QtCore.QCoreApplication.translate
        Dialog_newproject.setWindowTitle(_translate("Dialog_newproject", "New Show Control Project"))
        self.pushButtonselectfolder.setText(_translate("Dialog_newproject", "..."))
        self.label_projectfolder.setText(_translate("Dialog_newproject", "Project Folder:"))
        self.lineEdit_projectname.setToolTip(_translate("Dialog_newproject", "Project Name (Typically the name of the show or production.)"))
        self.label_projectname.setText(_translate("Dialog_newproject", "Project Name:"))
        self.label_cuefile.setText(_translate("Dialog_newproject", "Cue File:"))

