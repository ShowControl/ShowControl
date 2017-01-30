# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ScrollTabs-2_sans strips.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # mainwindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 640)
        # create a widget for the central widget whose parent is to main window
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # add layout to central widget
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        # create a tab widget and add it to central widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        # # create a tab widget
        # self.tab = QtWidgets.QWidget()
        # self.tab.setObjectName("tab")
        # # put a vertical layout on the tab
        # self.verticalLayout = QtWidgets.QVBoxLayout(self.tab)
        # self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        # self.verticalLayout.setObjectName("verticalLayout")
        # # add a scroll area to the tab
        # self.scrollArea = QtWidgets.QScrollArea(self.tab)
        # self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setObjectName("scrollArea")
        # # put a widget to contain the controls on the scroll area
        # self.scrollAreaWidgetContents = QtWidgets.QWidget()
        # self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 626, 450))
        # self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        # # put a grid layout on the scroll container widget
        # self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        # self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        # self.gridLayout_2.setObjectName("gridLayout_2")
        # self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        # self.verticalLayout.addWidget(self.scrollArea)
        # self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 668, 28))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Page"))


