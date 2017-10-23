# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NewProject_dlg-0.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName("NewProject")
        NewProject.resize(835, 558)
        self.gridLayout = QtWidgets.QGridLayout(NewProject)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(NewProject)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lineEdit_ProjectTitle = QtWidgets.QLineEdit(NewProject)
        self.lineEdit_ProjectTitle.setObjectName("lineEdit_ProjectTitle")
        self.gridLayout_2.addWidget(self.lineEdit_ProjectTitle, 2, 1, 1, 1)
        self.label_ProjectName = QtWidgets.QLabel(NewProject)
        self.label_ProjectName.setObjectName("label_ProjectName")
        self.gridLayout_2.addWidget(self.label_ProjectName, 1, 0, 1, 1)
        self.lineEdit_ProjectName = QtWidgets.QLineEdit(NewProject)
        self.lineEdit_ProjectName.setObjectName("lineEdit_ProjectName")
        self.gridLayout_2.addWidget(self.lineEdit_ProjectName, 1, 1, 1, 1)
        self.label_ProjectTitle = QtWidgets.QLabel(NewProject)
        self.label_ProjectTitle.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_ProjectTitle.setObjectName("label_ProjectTitle")
        self.gridLayout_2.addWidget(self.label_ProjectTitle, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 4, 1, 1, 1)
        self.label_HomeFolder = QtWidgets.QLabel(NewProject)
        self.label_HomeFolder.setObjectName("label_HomeFolder")
        self.gridLayout_2.addWidget(self.label_HomeFolder, 0, 0, 1, 1)
        self.lineEdit_HomeFolder = QtWidgets.QLineEdit(NewProject)
        self.lineEdit_HomeFolder.setReadOnly(True)
        self.lineEdit_HomeFolder.setObjectName("lineEdit_HomeFolder")
        self.gridLayout_2.addWidget(self.lineEdit_HomeFolder, 0, 1, 1, 1)
        self.lineEdit_ProjectVenue = QtWidgets.QLineEdit(NewProject)
        self.lineEdit_ProjectVenue.setObjectName("lineEdit_ProjectVenue")
        self.gridLayout_2.addWidget(self.lineEdit_ProjectVenue, 3, 1, 1, 1)
        self.label_ProjectVenue = QtWidgets.QLabel(NewProject)
        self.label_ProjectVenue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_ProjectVenue.setObjectName("label_ProjectVenue")
        self.gridLayout_2.addWidget(self.label_ProjectVenue, 3, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(NewProject)
        self.buttonBox.accepted.connect(NewProject.accept)
        self.buttonBox.rejected.connect(NewProject.reject)
        QtCore.QMetaObject.connectSlotsByName(NewProject)

    def retranslateUi(self, NewProject):
        _translate = QtCore.QCoreApplication.translate
        NewProject.setWindowTitle(_translate("NewProject", "New Project"))
        self.lineEdit_ProjectTitle.setToolTip(_translate("NewProject", "Enter project title."))
        self.label_ProjectName.setText(_translate("NewProject", "Project Name:"))
        self.lineEdit_ProjectName.setToolTip(_translate("NewProject", "Eneter project name."))
        self.label_ProjectTitle.setText(_translate("NewProject", "Title:"))
        self.label_HomeFolder.setText(_translate("NewProject", "Home Folder"))
        self.lineEdit_HomeFolder.setToolTip(_translate("NewProject", "Create project in this folder."))
        self.lineEdit_ProjectVenue.setToolTip(_translate("NewProject", "Enter venue name."))
        self.label_ProjectVenue.setText(_translate("NewProject", "Venue:"))

