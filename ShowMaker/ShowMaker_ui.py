# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ShowMaker.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow_showmaker(object):
    def setupUi(self, MainWindow_showmaker):
        MainWindow_showmaker.setObjectName("MainWindow_showmaker")
        MainWindow_showmaker.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow_showmaker)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_projectfolder = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_projectfolder.setObjectName("lineEdit_projectfolder")
        self.horizontalLayout.addWidget(self.lineEdit_projectfolder)
        self.pushButtonselectfolder = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonselectfolder.setMaximumSize(QtCore.QSize(27, 16777215))
        self.pushButtonselectfolder.setObjectName("pushButtonselectfolder")
        self.horizontalLayout.addWidget(self.pushButtonselectfolder)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 3, 0, 1, 1)
        self.label_projectfolder = QtWidgets.QLabel(self.centralwidget)
        self.label_projectfolder.setMaximumSize(QtCore.QSize(16777215, 28))
        self.label_projectfolder.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_projectfolder.setObjectName("label_projectfolder")
        self.gridLayout_2.addWidget(self.label_projectfolder, 1, 0, 1, 1)
        self.lineEdit_projectname = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_projectname.setObjectName("lineEdit_projectname")
        self.gridLayout_2.addWidget(self.lineEdit_projectname, 0, 1, 1, 1)
        self.label_projectname = QtWidgets.QLabel(self.centralwidget)
        self.label_projectname.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_projectname.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_projectname.setObjectName("label_projectname")
        self.gridLayout_2.addWidget(self.label_projectname, 0, 0, 1, 1)
        self.label_cuefile = QtWidgets.QLabel(self.centralwidget)
        self.label_cuefile.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_cuefile.setObjectName("label_cuefile")
        self.gridLayout_2.addWidget(self.label_cuefile, 2, 0, 1, 1)
        self.lineEdit_projectcuefile = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_projectcuefile.setObjectName("lineEdit_projectcuefile")
        self.gridLayout_2.addWidget(self.lineEdit_projectcuefile, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        MainWindow_showmaker.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow_showmaker)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 28))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        MainWindow_showmaker.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow_showmaker)
        self.statusbar.setObjectName("statusbar")
        MainWindow_showmaker.setStatusBar(self.statusbar)
        self.action_NewShow = QtWidgets.QAction(MainWindow_showmaker)
        self.action_NewShow.setObjectName("action_NewShow")
        self.action_OpenShow = QtWidgets.QAction(MainWindow_showmaker)
        self.action_OpenShow.setObjectName("action_OpenShow")
        self.action_SaveShow = QtWidgets.QAction(MainWindow_showmaker)
        self.action_SaveShow.setObjectName("action_SaveShow")
        self.action_CloseShow = QtWidgets.QAction(MainWindow_showmaker)
        self.action_CloseShow.setObjectName("action_CloseShow")
        self.action_Exit = QtWidgets.QAction(MainWindow_showmaker)
        self.action_Exit.setObjectName("action_Exit")
        self.menu_File.addAction(self.action_NewShow)
        self.menu_File.addAction(self.action_OpenShow)
        self.menu_File.addAction(self.action_SaveShow)
        self.menu_File.addAction(self.action_CloseShow)
        self.menu_File.addAction(self.action_Exit)
        self.menubar.addAction(self.menu_File.menuAction())

        self.retranslateUi(MainWindow_showmaker)
        QtCore.QMetaObject.connectSlotsByName(MainWindow_showmaker)

    def retranslateUi(self, MainWindow_showmaker):
        _translate = QtCore.QCoreApplication.translate
        MainWindow_showmaker.setWindowTitle(_translate("MainWindow_showmaker", "Show Maker"))
        self.pushButtonselectfolder.setText(_translate("MainWindow_showmaker", "..."))
        self.label_projectfolder.setText(_translate("MainWindow_showmaker", "Project Folder:"))
        self.lineEdit_projectname.setToolTip(_translate("MainWindow_showmaker", "Project Name (Typically the name of the show or production.)"))
        self.label_projectname.setText(_translate("MainWindow_showmaker", "Project Name:"))
        self.label_cuefile.setText(_translate("MainWindow_showmaker", "Cue File:"))
        self.menu_File.setTitle(_translate("MainWindow_showmaker", "&File"))
        self.action_NewShow.setText(_translate("MainWindow_showmaker", "&New Show"))
        self.action_OpenShow.setText(_translate("MainWindow_showmaker", "&Open Show"))
        self.action_SaveShow.setText(_translate("MainWindow_showmaker", "&Save Show"))
        self.action_CloseShow.setText(_translate("MainWindow_showmaker", "&Close Show"))
        self.action_Exit.setText(_translate("MainWindow_showmaker", "&Exit"))
