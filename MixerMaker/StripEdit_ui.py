# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StripEdit-1.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(604, 581)
        Dialog.setMaximumSize(QtCore.QSize(16777215, 16777212))
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(2)
        self.gridLayout.setVerticalSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_CommandString = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_CommandString.setObjectName("lineEdit_CommandString")
        self.gridLayout.addWidget(self.lineEdit_CommandString, 8, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.lineEdit_Name = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Name.setObjectName("lineEdit_Name")
        self.gridLayout.addWidget(self.lineEdit_Name, 2, 1, 3, 2)
        self.lineEdit_Count = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Count.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.lineEdit_Count.setObjectName("lineEdit_Count")
        self.gridLayout.addWidget(self.lineEdit_Count, 1, 1, 1, 2)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 3, 1)
        self.comboBox_StripType = QtWidgets.QComboBox(Dialog)
        self.comboBox_StripType.setMouseTracking(True)
        self.comboBox_StripType.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.comboBox_StripType.setEditable(False)
        self.comboBox_StripType.setObjectName("comboBox_StripType")
        self.comboBox_StripType.addItem("")
        self.comboBox_StripType.addItem("")
        self.comboBox_StripType.addItem("")
        self.comboBox_StripType.addItem("")
        self.comboBox_StripType.addItem("")
        self.comboBox_StripType.addItem("")
        self.comboBox_StripType.addItem("")
        self.gridLayout.addWidget(self.comboBox_StripType, 0, 1, 1, 2)
        self.comboBox_CommandType = QtWidgets.QComboBox(Dialog)
        self.comboBox_CommandType.setObjectName("comboBox_CommandType")
        self.comboBox_CommandType.addItem("")
        self.comboBox_CommandType.addItem("")
        self.comboBox_CommandType.addItem("")
        self.gridLayout.addWidget(self.comboBox_CommandType, 10, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.lineEdit_DefaultValue = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_DefaultValue.setObjectName("lineEdit_DefaultValue")
        self.gridLayout.addWidget(self.lineEdit_DefaultValue, 12, 1, 1, 1)
        self.tableView_ControlsInStrip = QtWidgets.QTableView(Dialog)
        self.tableView_ControlsInStrip.setObjectName("tableView_ControlsInStrip")
        self.tableView_ControlsInStrip.horizontalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableView_ControlsInStrip, 5, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 10, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 8, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 11, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 1)
        self.comboBox_ControlType = QtWidgets.QComboBox(Dialog)
        self.comboBox_ControlType.setObjectName("comboBox_ControlType")
        self.comboBox_ControlType.addItem("")
        self.comboBox_ControlType.addItem("")
        self.comboBox_ControlType.addItem("")
        self.gridLayout.addWidget(self.comboBox_ControlType, 6, 1, 1, 1)
        self.lineEdit_Range = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Range.setObjectName("lineEdit_Range")
        self.gridLayout.addWidget(self.lineEdit_Range, 11, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 12, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 13, 0, 1, 1)
        self.lineEdit_Anomalies = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Anomalies.setObjectName("lineEdit_Anomalies")
        self.gridLayout.addWidget(self.lineEdit_Anomalies, 13, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.label_7.setBuddy(self.comboBox_CommandType)
        self.label_6.setBuddy(self.lineEdit_CommandString)
        self.label_8.setBuddy(self.lineEdit_Range)
        self.label_4.setBuddy(self.comboBox_ControlType)
        self.label_9.setBuddy(self.lineEdit_DefaultValue)
        self.label_10.setBuddy(self.lineEdit_Anomalies)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.buttonBox, self.comboBox_StripType)
        Dialog.setTabOrder(self.comboBox_StripType, self.lineEdit_Count)
        Dialog.setTabOrder(self.lineEdit_Count, self.lineEdit_Name)
        Dialog.setTabOrder(self.lineEdit_Name, self.tableView_ControlsInStrip)
        Dialog.setTabOrder(self.tableView_ControlsInStrip, self.comboBox_ControlType)
        Dialog.setTabOrder(self.comboBox_ControlType, self.lineEdit_CommandString)
        Dialog.setTabOrder(self.lineEdit_CommandString, self.comboBox_CommandType)
        Dialog.setTabOrder(self.comboBox_CommandType, self.lineEdit_Range)
        Dialog.setTabOrder(self.lineEdit_Range, self.lineEdit_DefaultValue)
        Dialog.setTabOrder(self.lineEdit_DefaultValue, self.lineEdit_Anomalies)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Mixer Strip"))
        self.lineEdit_CommandString.setToolTip(_translate("Dialog", "Enter the osc or midi command string"))
        self.label_2.setText(_translate("Dialog", "Count"))
        self.label_3.setText(_translate("Dialog", "Strip Type"))
        self.lineEdit_Name.setToolTip(_translate("Dialog", "Strip name or header, typically Ch, Bus, Aux"))
        self.lineEdit_Count.setToolTip(_translate("Dialog", "Number of strips of this type, max = 99"))
        self.label.setText(_translate("Dialog", "Name"))
        self.comboBox_StripType.setToolTip(_translate("Dialog", "Select the strip type."))
        self.comboBox_StripType.setItemText(0, _translate("Dialog", "input"))
        self.comboBox_StripType.setItemText(1, _translate("Dialog", "auxin"))
        self.comboBox_StripType.setItemText(2, _translate("Dialog", "bus"))
        self.comboBox_StripType.setItemText(3, _translate("Dialog", "main"))
        self.comboBox_StripType.setItemText(4, _translate("Dialog", "stout"))
        self.comboBox_StripType.setItemText(5, _translate("Dialog", "auxmaster"))
        self.comboBox_StripType.setItemText(6, _translate("Dialog", "busmaster"))
        self.comboBox_CommandType.setToolTip(_translate("Dialog", "Select the command type."))
        self.comboBox_CommandType.setItemText(0, _translate("Dialog", "level"))
        self.comboBox_CommandType.setItemText(1, _translate("Dialog", "enum"))
        self.comboBox_CommandType.setItemText(2, _translate("Dialog", "string"))
        self.label_5.setText(_translate("Dialog", "Controls In Strip"))
        self.lineEdit_DefaultValue.setToolTip(_translate("Dialog", "Enter default value."))
        self.tableView_ControlsInStrip.setToolTip(_translate("Dialog", "Select control to edit or right click to add or remove."))
        self.label_7.setText(_translate("Dialog", "Command Type"))
        self.label_6.setText(_translate("Dialog", "Command String"))
        self.label_8.setText(_translate("Dialog", "Range"))
        self.label_4.setText(_translate("Dialog", "Control Type"))
        self.comboBox_ControlType.setToolTip(_translate("Dialog", "Select control type. (Only available for add)"))
        self.comboBox_ControlType.setItemText(0, _translate("Dialog", "fader"))
        self.comboBox_ControlType.setItemText(1, _translate("Dialog", "mute"))
        self.comboBox_ControlType.setItemText(2, _translate("Dialog", "scribble"))
        self.lineEdit_Range.setToolTip(_translate("Dialog", "Enter range, typically low,high,steps."))
        self.label_9.setText(_translate("Dialog", "Default Value"))
        self.label_10.setText(_translate("Dialog", "Anomalies"))
        self.lineEdit_Anomalies.setToolTip(_translate("Dialog", "Enter anomalies. "))

